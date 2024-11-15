# semaphore_playbooks
## Setup
For Mikrotik updates to work with **password**, modify file client.py in paramiko modules. Variable to look for are allow_agent and look_for_keys. They both have to be set to False.

```python
228        allow_agent=True, --> allow_agent=False,
229        look_for_keys=True, --> look_for_keys=False,
```

Create symbolic link to inventory directory

```bash
ln -sn /path/to/your/inventory inventory
```

### Ansible Playbooks

### Python Playbooks

### Bash Playbooks
