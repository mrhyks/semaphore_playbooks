from nornir import InitNornir
from nornir.core import Nornir
import yaml


def convert_to_hosts_dict(nr: Nornir) -> tuple[dict, dict, dict]:
    """
    Convert Nornir inventory to a list of host dictionaries and group dictionaries.
    Args:
        nr (Nornir): The Nornir object containing the inventory.
    Returns:
        tuple[list[dict], list[dict]]: A tuple containing two lists:
            - The first list contains dictionaries representing hosts.
            - The second list contains dictionaries representing groups for platforms and device roles.
    The function processes the Nornir inventory and extracts relevant information about hosts,
    platforms, and device roles. It creates groups for platforms and device roles if they do not
    already exist. Each host dictionary includes the hostname, associated groups, tags, and site
    information if available.
    """

    hosts: dict = {}
    groups: dict = {}

    ansible: dict = {"all": {"children": {}}}

    for name, host in nr.inventory.hosts.items():

        ### Create groups for platforms and device roles if they don't exist already.

        try:
            for group in groups:
                if host.data["platform"]["slug"] in group:
                    break
            else:
                groups[host.data["platform"]["slug"]] = {
                    "update_cmd": host.data["platform"]["custom_fields"]["update_cmd"]
                }

            for group in groups:
                if host.data["role"]["slug"] in group:
                    break
            else:
                groups[host.data["role"]["slug"]] = {"some_field": "N/A"}
        except:
            continue

        device_groups = []
        for group in host.groups:
            if "site" in group.name:
                site = group.name.split("__")[1]
            elif "device_role" in group.name or "platform" in group.name:
                device_groups.append(group.name.split("__")[1])

        tags = []
        for tag in host.data["tags"]:
            tags.append(tag["name"])

        host_dict = {
            "hostname": host.hostname,
            "groups": device_groups,
        }

        if tags:
            host_dict["tags"] = tags

        if site:
            host_dict["site"] = site

        hosts[host.name] = host_dict

        for group in device_groups:
            if group not in ansible["all"]["children"]:
                ansible["all"]["children"][group] = {"hosts": {}}
            ansible["all"]["children"][group]["hosts"][host.name]={'ansible_host':  host.data['primary_ip4']['address'].split('/')[0] if host.data['primary_ip4'] else None}
            
            for inner_group in device_groups:
                if inner_group != group:
                    if inner_group not in ansible["all"]["children"][group]["hosts"][host.name]:
                        ansible["all"]["children"][group]["hosts"][host.name]["groups"] = []
                    ansible["all"]["children"][group]["hosts"][host.name]["groups"].append(inner_group)
                        
        ansible["all"]["children"][host.data["platform"]["slug"]]["vars"] = {"update_cmd": host.data["platform"]["custom_fields"]["update_cmd"]}

    return hosts, groups, ansible


def main() -> None:

    nr = InitNornir(config_file="inventory/nb_inventory.yml")

    hosts, groups, ansible = convert_to_hosts_dict(nr)
    with open("~/semaphore_playbooks/inventory/hosts.yml", "w") as f:
        yaml.dump(hosts, f)

    with open("~/semaphore_playbooks/inventory/groups.yml", "w") as f:
        yaml.dump(groups, f)

    with open("~/semaphore_playbooks/inventory/ansible.yml", "w") as f:
        f.write("---\n")
        yaml.dump(ansible, f)


if __name__ == "__main__":
    main()
