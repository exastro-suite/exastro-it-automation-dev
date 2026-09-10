# Ansible Common Functions

## Ansible Driver Overview

### Ansible Core
An automation tool for platform construction. You describe processing in a Playbook and use modules to control various devices.

### Ansible Automation Controller
A platform that extends Ansible with management functions. You combine projects, inventories, and credentials to create and run job templates.

### Ansible Execution Agent
A server dedicated to Ansible execution, independent of ITA. It builds the execution environment with ansible-builder and runs it with ansible-runner. It is prepared per workspace and can be configured for redundancy.

### The Three Modes of Ansible Driver

1. **Legacy mode**: Applies settings using standard Ansible functionality. Construction code is registered as individual YAML files.
2. **Legacy Role mode**: Registers construction code as packages. Configurations are composed of combinations of Roles.
3. **Pioneer mode**: Allows interactive configuration entry using proprietary modules. Supports devices that can be logged in to via Telnet/SSH.

## Types of Variables

### Normal variables
Variables for which a single concrete value can be defined per variable name.

### Multiple-value variables
Variables for which multiple concrete values can be defined per variable name.

### Multi-level variables
Hierarchically structured variables. Available only in Ansible-LegacyRole.

### Global variables
Registered from `Ansible Common --> Global Variable Management`. Centrally manages information shared across multiple Playbooks or tasks.

### Global variables (sensitive)
Global variables that are stored encrypted. Used via ansible-vault. Used to manage sensitive information such as credentials and API keys.

### Template-embedded variables
Variables registered from `Ansible Common --> Template Management`.

### File-embedded variables
Variables registered from `Ansible Common --> File Management`.

### ITA-Specific Variables

#### Device list variables
- `__inventory_hostname__`: Host name
- `__dnshostname__`: DNS host name
- `__ipaddress__`: IP address
- `__loginprotocol__`: Protocol
- `__loginuser__`: Login user ID
- `__loginpassword__`: Login password

#### Movement ID
- `__movement_id__`: Movement ID from the Movement list

#### Operation
- `__operation__`: Operation information
- `__operation_datetime__`: Scheduled execution date/time
- `__operation_id__`: Operation ID
- `__operation_name__`: Operation name

#### Work instance ID
- `__execution_no__`: Work No. used for checking work status

#### Conductor instance ID
- `__conductor_id__`: Conductor instance ID used for checking Conductor work

#### Data linkage
- `__workflowdir__`: Work directory path
- `__conductor_workflowdir__`: Conductor work directory path (for sharing files between Movements)
- `__movement_status_filepath__`: Status file path
- `__parameters_dir_for_epc__`: Path to "_parameters" in the work directory (in)
- `__parameters_file_dir_for_epc__`: Path to "_parameters_file" in the work directory (in)
- `__parameter_dir__`: Path to "_parameters" in the work result directory (out)
- `__parameters_file_dir__`: Path to "_parameters_file" in the work result directory (out)

#### Organization management
- `__organization_id__`: Organization ID
- `__workspace_id__`: Workspace ID
- `__external_url__`: Public endpoint for the service

## Materials Targeted for Variable Extraction

- **Playbook Material Collection**: Playbook materials (Legacy)
- **Dialogue File Material Collection**: Dialogue file materials (Pioneer)
- **Role Package Management**: Role package files (LegacyRole)
- **Template Management**: Variable definitions (all modes)
- **Device List**: Additional inventory file options (Legacy, LegacyRole)
- **Movement List**: Header section (Legacy, LegacyRole)
- **Parameter Sheet**: Selected items in Template Management (all modes)

## Main Menus

- **Device List**: Manages the devices targeted for work
- **Interface Information**: Configures the Ansible execution method
- **Ansible Automation Platform Node List**: Manages AAP node information
- **Global Variable Management**: Centrally manages common variables
- **Global Variable (Sensitive) Management**: Manages encrypted confidential information
- **File Management**: Manages files used by Playbooks
- **Template Management**: Manages template files and their variables
- **Execution Environment Definition Template Management**: Manages templates for the execution environment
- **Execution Environment Management**: Manages the Ansible execution environment
- **Agent Management**: Manages the Ansible Execution Agent
- **Unmanaged Variable List**: Specifies variables to be excluded from variable extraction
