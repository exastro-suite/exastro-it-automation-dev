# Overview

## What is Exastro IT Automation?
Exastro IT Automation is an open source framework for digitizing and centrally managing system configuration.
It can manage information related to system configuration, such as device information, configuration values, and work history, and this information can be output as Excel data.
It also has functions to manage and execute, as workflows, the system construction and operational configuration of each device, and it can be integrated with a variety of platform construction tools.

## Features
It is equipped with RBAC (Role-based access control), which allows you to define roles such as developer, worker, and operator, and
:Group and manage the history of parameters:
you can group and manage the history of the system's parameter information.
:Analyze IaC and extract variables:
When Infrastructure as Code (IaC) is uploaded, it is first analyzed to check whether the IaC contains any errors. If there are no errors, the variable names are extracted from the IaC description and managed.
Because variable names are selected from a list, human errors such as typos do not occur.
:Manage IaC as modules to improve reusability:
So that IaC (such as Playbooks) is not used only once and discarded but can continue to be reused, it can be modularized and assembled at the time of work.
You can connect multiple automation software tools to define a single work flow. It also automatically generates the input data required for the automation software to operate.
Example (in the case of Ansible): Gather and connect the required Playbooks, and create host_vars from parameters for each node.
It also thoroughly manages work records, for example by allowing you to download the execution results (work evidence) whenever you need them.

## Functions
:Management Console function:
The management console handles control of the users who use the system (registration/update/deletion) and access control for operation menus (registration/update/deletion).
It performs import/export of the various data managed by Exastro IT Automation.
:Build Material Management function:
Manages the IaC used by automation software (OSS).
On the backend, it works together with Git, while on the frontend it provides status management for checkout/return.
:Basic Console function:
The basic console provides the functions that are commonly required when working with Exastro IT Automation.
- Registration and management of device information (device list)
- Creation, management, and execution of Conductors (job flows)
:Parameter/Host Group function:
Provides functions for centrally managing and tracking the history of the system configuration (parameters for each host or host group).
The parameters to be managed can be freely defined.
Parameter values can be linked to variables in IaC (such as Playbooks).
Provides an interface for controlling IaC (such as Playbooks) for each automation software.
The behavior of automation software can be encapsulated in a Movement (a unit of work), and these can be linked together as a Conductor (job flow).
  - What is a Movement?
    - | This is the unit of work, such as construction and configuration, performed on each device using a construction tool.
  - What is a Conductor?
    - | This is a unit for a series of tasks. It is executed in association with an operation name.
By combining various parts called Nodes, you create a job flow and perform a series of construction, configuration, and other tasks on multiple devices.
  - What is an Operation?
    - | This is a work execution unit. It is possible to manage work schedules, execution history, and other information.
