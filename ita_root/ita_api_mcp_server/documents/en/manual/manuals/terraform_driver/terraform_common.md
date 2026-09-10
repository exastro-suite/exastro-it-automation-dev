# Terraform driver Common
# Introduction
This document describes the functions common to "" "" (hereafter, Terraform driver).
# Overview

## About Terraform
Also, with Terraform Cloud and Terraform Enterprise, it is possible to manage access policies as code using Policy as Code.

## About Terraform driver
Terraform driver, as a function of ITA, can execute Terraform and retrieve execution logs.
The Module files used to execute work (Plan/Apply) and the Policy files used to perform PolicyCheck can be modularized and managed for reuse on ITA.
-  | **Terraform Cloud/EP driver**
For the Terraform Cloud or Terraform Enterprise registered in ITA, you can create Organizations, create Workspaces, execute work (Plan/PolicyCheck/Apply), and retrieve work logs.
For details on the operation method, refer to "".
-  | **Terraform CLI driver**
For details on the operation method, refer to "".
# Handling Variables

## Types of Variables
※For details on the setting method, refer to " -> " " -> ".
Targets defined in a Variable block within a Module file can be treated as variables.
Normal variable | A variable for which a concrete value can be defined for the variable name.               |
Variables within a Module must be described according to the variable rules of HCL (HashiCorp Configuration Language)\|
In this case, "xxx" is extracted from the Module as a variable.      |
Also, type and default values can be set.          |
Setting type and default is not mandatory.                |

## Variable Extraction and Concrete Value Registration
Variables can be extracted from Module materials uploaded to ITA, and concrete values can be registered for them.
The concrete values of extracted variables are registered by linking them with a parameter sheet at " -> " " -> ".
In Terraform Cloud/EP driver, the registered variables and concrete values are registered, at work execution time, in the Variables managed by the Workspace of the linked Terraform, with the "variable name" as "Key" and the "concrete value" as "Value".
In Terraform CLI driver, the registered variables and concrete values are written, at work execution time, into the generated terraform.tfvars file with the "variable name" as "Key" and the "concrete value" as "Value", and are used during work execution.

## About Variable Types
A type can be set within a variable.
Variables within a Module must be described according to the variable rules of HCL (HashiCorp Configuration Language).
The variables handled within ITA are as follows.
.. list-table:: Variable types
- type
     - Details
     - | Member variable target
     - | Assignment order target
     - Example of type description
     - Example of default description
- string
     - String type.
     - x
     - x
     - string
     - abc
- number
     - Number type.
     - x
     - x
     - number
     - 123
- bool
     - Boolean type (true or false).
     - x
     - x
     - bool
     - true
- list
     - Array type.
     - x
     - o
     - list(string)
     - ["a", "b", "c"]
- set
     - | Array type. Requires unique values to be set.
     - x
     - o
     - set(number)
     - [1, 2, 3]
- tuple
     - | Array type. The type to be set for the nth position must be decided in advance.
Because the number of input values is fixed, on the IT System A it is selected as a member variable from a pulldown.
     - o
     - x
     - tuple([string, number])
     - ["abc", 2023]
- map
     - | Key-value (associative array) type. On ITA, when a type is set that includes one or more map types, the key value cannot be identified from the type information, so HCL setting must be turned ON when performing automatic assignment value registration setting.
For details on HCL setting, refer to "".
     - x
     - x
     - map(string)
     - {"test_key" = "test_value"}
- object
     - | Key-value (associative array) type. On ITA, the key name is treated as a member variable. Do not include Japanese characters in the key name.
     - o
     - x
     - object({test_key = string})
     - {"test_key" = "test_value"}
- any
     - A type that matches anything, but on ITA it is treated the same as the string type.
     - x
     - x
     - any
     - abc
- Not specified
     - If type is not specified, it is treated the same as the string type on ITA.
     - x
     - x
     -
     - abc
-  | **※1 ... Member variable target**
This is the key name when the variable is of key-value type.
If the variable type is object, the <KEY> of <KEY> = <TYPE> becomes the member variable.
If the variable type is tuple, the variables defined within the tuple are numbered from the beginning as [0],[1],[2]... and become member variables.
If the variable type is a target registered in the Variable Nesting Management menu, they are numbered as [0],[1],[2]... based on the maximum iteration count and become member variables.
For details on variable nesting, refer to " -> " " -> ".
      - | **Example: When the variable type is object**
1. tf file and registered value
1. Example assignment value (Automatic Assignment Value Registration Setting)
- No.
              - Variable name
              - Member variable
              - Assignment order
              - Parameter sheet input value
- 1
              -  VAR_hoge
              -  NAME
              -  Not enterable
              -  my_machine
- 2
              - VAR_hoge
              - IP
              - Not enterable
              - 192.168.100.1
1. Value sent to Terraform
      -  | **Example: When the variable type is tuple**
1. tf file and registered value
1. Example assignment value (Automatic Assignment Value Registration Setting)
- No.
              - Variable name
              - Member variable
              - Assignment order
              - Parameter sheet input value
- 1
              -  VAR_hoge
              -  [0]
              -  Not enterable
              -  def
- 2
              -  VAR_hoge
              -  [1]
              -  Not enterable
              -  2024
1. Value sent to Terraform
      -  | **Example: When the variable type is a nesting management target**
1. tf file and registered value
1. Example assignment value (Automatic Assignment Value Registration Setting)
- No.
              - Variable name
              - Member variable
              - Assignment order
              - Parameter sheet input value
- 1
              -  VAR_hoge
              -  [0]
              -  1
              -  aaa
- 2
              -  VAR_hoge
              -  [0]
              -  2
              -  bbb
- 3
              - VAR_hoge
              - [1]
              - 1
              - ccc
- 4
              - VAR_hoge
              - [1]
              - 2
              - ddd
1. Value sent to Terraform
-  | **※2 ... Assignment order target**
This is the order, starting from the beginning, in which multiple concrete values are assigned to a variable.
If the variable, or the lowest-level variable of a hierarchically structured variable, is of type list or set, this can be set at " -> " " -> ".
      -  | **Example: When the variable type is list**
1. tf file and registered value
1. Example assignment value (Automatic Assignment Value Registration Setting)
- No.
              - Variable name
              - Member variable
              - Assignment order
              - Parameter sheet input value
- 1
              -  VAR_hoge
              -  Not required
              -  1
              -  abc
- 2
              - VAR_hoge
              - Not required
              - 2
              - def
1. Value sent to Terraform
      -  | **Example: When the lowest-level variable of a hierarchically structured variable is of type set**
1. tf file and registered value
1. Example assignment value (Automatic Assignment Value Registration Setting)
- No.
              - Variable name
              - Member variable
              - Assignment order
              - Parameter sheet input value
- 1
              -  VAR_hoge
              -  key
              -  1
              -  1
- 2
              - VAR_hoge
              - key
              - 2
              - 2
1. Value sent to Terraform
# How to Write Construction Code
Policy is a function that is valid only for Terraform Cloud/EP driver.

## Writing the Module

## Writing the Policy
# Appendix

## Examples of Filling In and Registering the Module Material "Variable Block"
Examples of filling in the "Variable block" of a Module material and examples of registering it into the Automatic Assignment Value Registration Setting are described for each variable type.
1. **Simple patterns**
1. string type
1. number type
1. bool type
1. list type
1. set type
1. tuple type
1. map type
1. object type
1. any type
1. No type specified
1. **Complex patterns**
1. list type within a list type
1. object type within a list type
1. object type within a list type within an object type
1. **Special patterns**
1. map type within a list type

## Example Variable Nesting Management Flow
Describes operation examples for Variable Nesting Management.
1. **Increasing the maximum iteration count**
1. **Decreasing the maximum iteration count**
