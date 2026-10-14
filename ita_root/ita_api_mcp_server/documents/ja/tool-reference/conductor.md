# conductor tool reference
ITAの各種ドライバーで動作するMovementを、連続や並列、条件分岐を通り抜ける組み合わせで作成・実行します。

## Minimal conductor_data Example
```json
{
    "conductor": {
        "conductor_name": "sample conductor",
        "grid_snap": true,
        "id": "auto-increment id of conductor",
        "last_update_date_time": "2026/12/31 23:59:59.000000",
        "movement_white_space": "wrap",
        "movement_width": "auto",
        "note": null,
        "notice_info": {}
    },
    "config": {
        "edgeNumber": 3,
        "editorVersion": "2.0.0",
        "nodeNumber": 4,
        "terminalNumber": 5
    },
    "line-1": {
        "id": "line-1",
        "inNode": "node-3",
        "inTerminal": "terminal-3",
        "outNode": "node-1",
        "outTerminal": "terminal-1",
        "type": "edge"
    },
    "line-2": {
        "id": "line-2",
        "inNode": "node-2",
        "inTerminal": "terminal-2",
        "outNode": "node-3",
        "outTerminal": "terminal-4",
        "type": "edge"
    },
    "node-1": {
        "h": 58,
        "id": "node-1",
        "terminal": {
            "terminal-1": {
                "edge": "line-1",
                "id": "terminal-1",
                "targetNode": "node-3",
                "type": "out",
                "x": 7781,
                "y": 8000
            }
        },
        "type": "start",
        "w": 198.194,
        "x": 7600,
        "y": 7971.3335
    },
    "node-2": {
        "end_type": "6",
        "h": 58,
        "id": "node-2",
        "terminal": {
            "terminal-2": {
                "edge": "line-2",
                "id": "terminal-2",
                "targetNode": "node-3",
                "type": "in",
                "x": 8218,
                "y": 8000
            }
        },
        "type": "end",
        "w": 198.194,
        "x": 8200.917000000001,
        "y": 7971.3335
    },
    "node-3": {
        "h": 58,
        "id": "node-3",
        "movement_id": "auto increment id of movement",
        "movement_name": "sample movement",
        "operation_id": null,
        "orchestra_id": "1",
        "skip_flag": 0,
        "terminal": {
            "terminal-3": {
                "edge": "line-1",
                "id": "terminal-3",
                "targetNode": "node-1",
                "type": "in",
                "x": 7917,
                "y": 8000
            },
            "terminal-4": {
                "edge": "line-2",
                "id": "terminal-4",
                "targetNode": "node-2",
                "type": "out",
                "x": 8127,
                "y": 8000
            }
        },
        "type": "movement",
        "w": 244.417,
        "x": 7900,
        "y": 7971
    }
}
```

## Minimal conductor_data Example using Conductor Control
```json
{
    "conductor": {
        "conductor_name": "sample conductor",
        "grid_snap": true,
        "id": "auto-increment id of conductor",
        "last_update_date_time": "2026/12/31 23:59:59.000000",
        "movement_white_space": "wrap",
        "movement_width": "auto",
        "note": null,
        "notice_info": {}
    },
    "config": {
        "edgeNumber": 3,
        "editorVersion": "2.0.0",
        "nodeNumber": 4,
        "terminalNumber": 5
    },
    "line-1": {
        "id": "line-1",
        "inNode": "node-3",
        "inTerminal": "terminal-3",
        "outNode": "node-1",
        "outTerminal": "terminal-1",
        "type": "edge"
    },
    "line-2": {
        "id": "line-2",
        "inNode": "node-2",
        "inTerminal": "terminal-2",
        "outNode": "node-3",
        "outTerminal": "terminal-4",
        "type": "edge"
    },
    "node-1": {
        "h": 58,
        "id": "node-1",
        "terminal": {
            "terminal-1": {
                "edge": "line-1",
                "id": "terminal-1",
                "targetNode": "node-3",
                "type": "out",
                "x": 7781,
                "y": 8000
            }
        },
        "type": "start",
        "w": 198.194,
        "x": 7600,
        "y": 7971.3335
    },
    "node-2": {
        "end_type": "6",
        "h": 58,
        "id": "node-2",
        "terminal": {
            "terminal-2": {
                "edge": "line-2",
                "id": "terminal-2",
                "targetNode": "node-3",
                "type": "in",
                "x": 8218,
                "y": 8000
            }
        },
        "type": "end",
        "w": 198.194,
        "x": 8200.917000000001,
        "y": 7971.3335
    },
    "node-3": {
        "call_conductor_id": "auto-increment id of conductor",
        "call_conductor_name": "sample conductor called",
        "h": 58,
        "id": "node-3",
        "operation_id": null,
        "skip_flag": 0,
        "terminal": {
            "terminal-3": {
                "edge": "line-1",
                "id": "terminal-3",
                "targetNode": "node-1",
                "type": "in",
                "x": 7917,
                "y": 8000
            },
            "terminal-4": {
                "edge": "line-2",
                "id": "terminal-4",
                "targetNode": "node-2",
                "type": "out",
                "x": 8127,
                "y": 8000
            }
        },
        "type": "call",
        "w": 244.417,
        "x": 7900,
        "y": 7971
    }
}
```

## Minimal parallel exection conductor_data Example
```json
{
    "conductor": {
        "conductor_name": "sample conductor",
        "grid_snap": true,
        "id": "auto-increment id of conductor",
        "last_update_date_time": "2026/12/31 23:59:59.000000",
        "movement_white_space": "wrap",
        "movement_width": "auto",
        "note": null,
        "notice_info": {}
    },
    "config": {
        "edgeNumber": 7,
        "editorVersion": "2.0.0",
        "nodeNumber": 7,
        "terminalNumber": 13
    },
    "line-1": {
        "id": "line-1",
        "inNode": "node-4",
        "inTerminal": "terminal-5",
        "outNode": "node-1",
        "outTerminal": "terminal-1",
        "type": "edge"
    },
    "line-2": {
        "id": "line-2",
        "inNode": "node-3",
        "inTerminal": "terminal-3",
        "outNode": "node-4",
        "outTerminal": "terminal-6",
        "type": "edge"
    },
    "line-3": {
        "id": "line-3",
        "inNode": "node-5",
        "inTerminal": "terminal-8",
        "outNode": "node-3",
        "outTerminal": "terminal-4",
        "type": "edge"
    },
    "line-4": {
        "id": "line-4",
        "inNode": "node-2",
        "inTerminal": "terminal-2",
        "outNode": "node-5",
        "outTerminal": "terminal-10",
        "type": "edge"
    },
    "line-5": {
        "id": "line-5",
        "inNode": "node-6",
        "inTerminal": "terminal-11",
        "outNode": "node-4",
        "outTerminal": "terminal-7",
        "type": "edge"
    },
    "line-6": {
        "id": "line-6",
        "inNode": "node-5",
        "inTerminal": "terminal-9",
        "outNode": "node-6",
        "outTerminal": "terminal-12",
        "type": "edge"
    },
    "node-1": {
        "h": 58,
        "id": "node-1",
        "terminal": {
            "terminal-1": {
                "edge": "line-1",
                "id": "terminal-1",
                "targetNode": "node-4",
                "type": "out",
                "x": 7642,
                "y": 8000
            }
        },
        "type": "start",
        "w": 198.194,
        "x": 7461,
        "y": 7971.3335
    },
    "node-2": {
        "end_type": "6",
        "h": 58,
        "id": "node-2",
        "terminal": {
            "terminal-2": {
                "edge": "line-4",
                "id": "terminal-2",
                "targetNode": "node-5",
                "type": "in",
                "x": 8467,
                "y": 8000
            }
        },
        "type": "end",
        "w": 198.194,
        "x": 8450,
        "y": 7971
    },
    "node-3": {
        "h": 58,
        "id": "node-3",
        "movement_id": "auto increment id of movement",
        "movement_name": "sample movement",
        "operation_id": null,
        "orchestra_id": "1",
        "skip_flag": 0,
        "terminal": {
            "terminal-3": {
                "edge": "line-2",
                "id": "terminal-3",
                "targetNode": "node-4",
                "type": "in",
                "x": 7917,
                "y": 7950
            },
            "terminal-4": {
                "edge": "line-3",
                "id": "terminal-4",
                "targetNode": "node-5",
                "type": "out",
                "x": 8127,
                "y": 7950
            }
        },
        "type": "movement",
        "w": 244.417,
        "x": 7900,
        "y": 7921
    },
    "node-4": {
        "h": 116,
        "id": "node-4",
        "terminal": {
            "terminal-5": {
                "edge": "line-1",
                "id": "terminal-5",
                "targetNode": "node-1",
                "type": "in",
                "x": 7717,
                "y": 7997
            },
            "terminal-6": {
                "case": 1,
                "edge": "line-2",
                "id": "terminal-6",
                "targetNode": "node-3",
                "type": "out",
                "x": 7817,
                "y": 7956
            },
            "terminal-7": {
                "case": 2,
                "edge": "line-5",
                "id": "terminal-7",
                "targetNode": "node-6",
                "type": "out",
                "x": 7817,
                "y": 8038
            }
        },
        "type": "parallel-branch",
        "w": 134,
        "x": 7700,
        "y": 7939.4445
    },
    "node-5": {
        "h": 116,
        "id": "node-5",
        "terminal": {
            "terminal-10": {
                "edge": "line-4",
                "id": "terminal-10",
                "targetNode": "node-2",
                "type": "out",
                "x": 8393,
                "y": 7997
            },
            "terminal-8": {
                "case": 1,
                "edge": "line-3",
                "id": "terminal-8",
                "targetNode": "node-3",
                "type": "in",
                "x": 8217,
                "y": 7956
            },
            "terminal-9": {
                "case": 2,
                "edge": "line-6",
                "id": "terminal-9",
                "targetNode": "node-6",
                "type": "in",
                "x": 8217,
                "y": 8038
            }
        },
        "type": "merge",
        "w": 210.125,
        "x": 8200,
        "y": 7939.4445
    },
    "node-6": {
        "h": 58,
        "id": "node-6",
        "movement_id": "auto increment id of movement",
        "movement_name": "sample movement",
        "operation_id": null,
        "orchestra_id": "1",
        "skip_flag": 0,
        "terminal": {
            "terminal-11": {
                "edge": "line-5",
                "id": "terminal-11",
                "targetNode": "node-4",
                "type": "in",
                "x": 7917,
                "y": 8050
            },
            "terminal-12": {
                "edge": "line-6",
                "id": "terminal-12",
                "targetNode": "node-5",
                "type": "out",
                "x": 8127,
                "y": 8050
            }
        },
        "type": "movement",
        "w": 244.417,
        "x": 7900,
        "y": 8021
    }
}
```

## Minimal conductor_data Example using conditional branch
```json
{
    "conductor": {
        "conductor_name": "sample conductor",
        "grid_snap": true,
        "id": "auto-increment id of conductor",
        "last_update_date_time": "2026/12/31 23:59:59.000000",
        "movement_white_space": "wrap",
        "movement_width": "auto",
        "note": null,
        "notice_info": {}
    },
    "config": {
        "edgeNumber": 6,
        "editorVersion": "2.0.0",
        "nodeNumber": 7,
        "terminalNumber": 14
    },
    "line-1": {
        "id": "line-1",
        "inNode": "node-4",
        "inTerminal": "terminal-9",
        "outNode": "node-1",
        "outTerminal": "terminal-1",
        "type": "edge"
    },
    "line-2": {
        "id": "line-2",
        "inNode": "node-3",
        "inTerminal": "terminal-6",
        "outNode": "node-4",
        "outTerminal": "terminal-10",
        "type": "edge"
    },
    "line-3": {
        "id": "line-3",
        "inNode": "node-5",
        "inTerminal": "terminal-11",
        "outNode": "node-3",
        "outTerminal": "terminal-7",
        "type": "edge"
    },
    "line-4": {
        "id": "line-4",
        "inNode": "node-2",
        "inTerminal": "terminal-2",
        "outNode": "node-5",
        "outTerminal": "terminal-12",
        "type": "edge"
    },
    "line-5": {
        "id": "line-5",
        "inNode": "node-6",
        "inTerminal": "terminal-13",
        "outNode": "node-3",
        "outTerminal": "terminal-8",
        "type": "edge"
    },
    "node-1": {
        "h": 58,
        "id": "node-1",
        "terminal": {
            "terminal-1": {
                "edge": "line-1",
                "id": "terminal-1",
                "targetNode": "node-4",
                "type": "out",
                "x": 7642,
                "y": 8000
            }
        },
        "type": "start",
        "w": 198.194,
        "x": 7461,
        "y": 7971.3335
    },
    "node-2": {
        "end_type": "6",
        "h": 58,
        "id": "node-2",
        "terminal": {
            "terminal-2": {
                "edge": "line-4",
                "id": "terminal-2",
                "targetNode": "node-5",
                "type": "in",
                "x": 8567,
                "y": 7950
            }
        },
        "type": "end",
        "w": 198.194,
        "x": 8550,
        "y": 7921
    },
    "node-3": {
        "h": 119.556,
        "id": "node-3",
        "terminal": {
            "terminal-6": {
                "edge": "line-2",
                "id": "terminal-6",
                "targetNode": "node-4",
                "type": "in",
                "x": 8017,
                "y": 7997
            },
            "terminal-7": {
                "case": 1,
                "condition": [
                    "5"
                ],
                "edge": "line-3",
                "id": "terminal-7",
                "targetNode": "node-5",
                "type": "out",
                "x": 8193,
                "y": 7956
            },
            "terminal-8": {
                "case": 2,
                "condition": [
                    "9999"
                ],
                "edge": "line-5",
                "id": "terminal-8",
                "targetNode": "node-6",
                "type": "out",
                "x": 8193,
                "y": 8039
            }
        },
        "type": "conditional-branch",
        "w": 209.542,
        "x": 8000,
        "y": 7937.6665
    },
    "node-4": {
        "h": 58,
        "id": "node-4",
        "movement_id": "auto increment id of movement",
        "movement_name": "sample movement",
        "operation_id": null,
        "orchestra_id": "1",
        "skip_flag": 0,
        "terminal": {
            "terminal-10": {
                "edge": "line-2",
                "id": "terminal-10",
                "targetNode": "node-3",
                "type": "out",
                "x": 7927,
                "y": 8000
            },
            "terminal-9": {
                "edge": "line-1",
                "id": "terminal-9",
                "targetNode": "node-1",
                "type": "in",
                "x": 7717,
                "y": 8000
            }
        },
        "type": "movement",
        "w": 244.417,
        "x": 7700,
        "y": 7971
    },
    "node-5": {
        "h": 58,
        "id": "node-5",
        "movement_id": "auto increment id of movement",
        "movement_name": "sample movement",
        "operation_id": null,
        "orchestra_id": "1",
        "skip_flag": 0,
        "terminal": {
            "terminal-11": {
                "edge": "line-3",
                "id": "terminal-11",
                "targetNode": "node-3",
                "type": "in",
                "x": 8267,
                "y": 7950
            },
            "terminal-12": {
                "edge": "line-4",
                "id": "terminal-12",
                "targetNode": "node-2",
                "type": "out",
                "x": 8477,
                "y": 7950
            }
        },
        "type": "movement",
        "w": 244.417,
        "x": 8250,
        "y": 7921
    },
    "node-6": {
        "end_type": "6",
        "h": 58,
        "id": "node-6",
        "terminal": {
            "terminal-13": {
                "edge": "line-5",
                "id": "terminal-13",
                "targetNode": "node-3",
                "type": "in",
                "x": 8567,
                "y": 8050
            }
        },
        "type": "end",
        "w": 198.194,
        "x": 8550,
        "y": 8021
    }
}
```

## Minimal conductor_data Example using status file branch
```json
{
    "conductor": {
        "conductor_name": "sample conductor",
        "grid_snap": true,
        "id": "auto-increment id of conductor",
        "last_update_date_time": "2026/12/31 23:59:59.000000",
        "movement_white_space": "wrap",
        "movement_width": "auto",
        "note": null,
        "notice_info": {}
    },
    "config": {
        "edgeNumber": 6,
        "editorVersion": "2.0.0",
        "nodeNumber": 7,
        "terminalNumber": 11
    },
    "line-1": {
        "id": "line-1",
        "inNode": "node-4",
        "inTerminal": "terminal-6",
        "outNode": "node-1",
        "outTerminal": "terminal-1",
        "type": "edge"
    },
    "line-2": {
        "id": "line-2",
        "inNode": "node-3",
        "inTerminal": "terminal-3",
        "outNode": "node-4",
        "outTerminal": "terminal-7",
        "type": "edge"
    },
    "line-3": {
        "id": "line-3",
        "inNode": "node-5",
        "inTerminal": "terminal-8",
        "outNode": "node-3",
        "outTerminal": "terminal-4",
        "type": "edge"
    },
    "line-4": {
        "id": "line-4",
        "inNode": "node-2",
        "inTerminal": "terminal-2",
        "outNode": "node-3",
        "outTerminal": "terminal-5",
        "type": "edge"
    },
    "line-5": {
        "id": "line-5",
        "inNode": "node-6",
        "inTerminal": "terminal-10",
        "outNode": "node-5",
        "outTerminal": "terminal-9",
        "type": "edge"
    },
    "node-1": {
        "h": 58,
        "id": "node-1",
        "terminal": {
            "terminal-1": {
                "edge": "line-1",
                "id": "terminal-1",
                "targetNode": "node-4",
                "type": "out",
                "x": 7581,
                "y": 8000
            }
        },
        "type": "start",
        "w": 198.194,
        "x": 7400,
        "y": 7971
    },
    "node-2": {
        "end_type": "6",
        "h": 58,
        "id": "node-2",
        "terminal": {
            "terminal-2": {
                "edge": "line-4",
                "id": "terminal-2",
                "targetNode": "node-3",
                "type": "in",
                "x": 8617,
                "y": 8050
            }
        },
        "type": "end",
        "w": 198.194,
        "x": 8600,
        "y": 8021
    },
    "node-3": {
        "h": 164,
        "id": "node-3",
        "terminal": {
            "terminal-3": {
                "edge": "line-2",
                "id": "terminal-3",
                "targetNode": "node-4",
                "type": "in",
                "x": 7967,
                "y": 7997
            },
            "terminal-4": {
                "case": 1,
                "condition": [
                    "SAMPLE"
                ],
                "edge": "line-3",
                "id": "terminal-4",
                "targetNode": "node-5",
                "type": "out",
                "x": 8243,
                "y": 7944
            },
            "terminal-5": {
                "case": "else",
                "edge": "line-4",
                "id": "terminal-5",
                "targetNode": "node-2",
                "type": "out",
                "x": 8243,
                "y": 8050
            }
        },
        "type": "status-file-branch",
        "w": 310,
        "x": 7950,
        "y": 7915.4445
    },
    "node-4": {
        "h": 58,
        "id": "node-4",
        "movement_id": "auto increment id of movement",
        "movement_name": "sample movement",
        "operation_id": null,
        "orchestra_id": "1",
        "skip_flag": 0,
        "terminal": {
            "terminal-6": {
                "edge": "line-1",
                "id": "terminal-6",
                "targetNode": "node-1",
                "type": "in",
                "x": 7667,
                "y": 8000
            },
            "terminal-7": {
                "edge": "line-2",
                "id": "terminal-7",
                "targetNode": "node-3",
                "type": "out",
                "x": 7891,
                "y": 8000
            }
        },
        "type": "movement",
        "w": 257.778,
        "x": 7650,
        "y": 7971
    },
    "node-5": {
        "h": 58,
        "id": "node-5",
        "movement_id": "auto increment id of movement",
        "movement_name": "sample movement",
        "operation_id": null,
        "orchestra_id": "1",
        "skip_flag": 0,
        "terminal": {
            "terminal-8": {
                "edge": "line-3",
                "id": "terminal-8",
                "targetNode": "node-3",
                "type": "in",
                "x": 8317,
                "y": 7950
            },
            "terminal-9": {
                "edge": "line-5",
                "id": "terminal-9",
                "targetNode": "node-6",
                "type": "out",
                "x": 8541,
                "y": 7950
            }
        },
        "type": "movement",
        "w": 257.778,
        "x": 8300,
        "y": 7921
    },
    "node-6": {
        "end_type": "6",
        "h": 58,
        "id": "node-6",
        "terminal": {
            "terminal-10": {
                "edge": "line-5",
                "id": "terminal-10",
                "targetNode": "node-5",
                "type": "in",
                "x": 8617,
                "y": 7950
            }
        },
        "type": "end",
        "w": 198.194,
        "x": 8600,
        "y": 7921
    }
}
```