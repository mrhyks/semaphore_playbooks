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

    ansible: dict = {}

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
            if group not in ansible:
                ansible[group] = {"hosts": {}}
            ansible[group]["hosts"][host.name]={'ansible_host':  host.data['primary_ip4']['address'].split('/')[0] if host.data['primary_ip4'] else None}
            
        ansible[host.data["platform"]["slug"]]["vars"] = {"update_cmd": host.data["platform"]["custom_fields"]["update_cmd"]}

    return hosts, groups, ansible


def main() -> None:

    nr = InitNornir(config_file="inventory/nb_inventory.yml")

    hosts, groups, ansible = convert_to_hosts_dict(nr)
    with open("inventory/hosts.yml", "w") as f:
        yaml.dump(hosts, f)

    with open("inventory/groups.yml", "w") as f:
        yaml.dump(groups, f)

    with open("inventory/ansible.yml", "w") as f:
        yaml.dump(ansible, f)


if __name__ == "__main__":
    main()
