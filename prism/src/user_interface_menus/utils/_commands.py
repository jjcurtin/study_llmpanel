def init_commands():
    from user_interface_menus._main_menu import main_menu, README

    # ------------------------------------------------------------
        
    from user_interface_menus.check._system_check_menu import system_check_menu, DIAGNOSTICS

    # ------------------------------------------------------------

    from user_interface_menus.tasks._system_task_menu import system_task_menu
    from user_interface_menus.tasks._system_task_menu import ADD_TASK, ADD_SYSTEM_TASK, ADD_R_SCRIPT
    from user_interface_menus.tasks._system_task_menu import REMOVE_TASK, CLEAR_TASKS
    from user_interface_menus.tasks._system_task_menu import EXECUTE_TASK, EXECUTE_SYSTEM_TASK, EXECUTE_R_SCRIPT

    # ------------------------------------------------------------

    from user_interface_menus.participants._participant_management_menus import participant_management_menu
    from user_interface_menus.participants._participant_management_menus import ADD_PARTICIPANT, PARTICIPANT_REFRESH, PARTICIPANT_ANNOUNCEMENT

    # ------------------------------------------------------------

    from user_interface_menus.logs._log_menu import log_menu
    from user_interface_menus.logs._log_menu import PRINT_TRANSCRIPT

    # ------------------------------------------------------------

    from user_interface_menus._shutdown_menu import shutdown_menu

    # ------------------------------------------------------------

    from user_interface_menus.help._help_menu import help_menu
    from user_interface_menus.help._help_menu import GENERAL_INFORMATION
    from user_interface_menus.help._developer_documentation import developer_documentation
    from user_interface_menus.help._research_assistant_documentation import research_assistant_documentation

    # ------------------------------------------------------------

    from user_interface_menus.settings._settings_menu import settings_menu
    from user_interface_menus.settings._settings_menu import DISPLAY, WINDOW_WIDTH_SETTINGS, PARAM_RELATED_THRESHOLD, PARAM_ASSISTANT_TEMPERATURE, SYSTEM_SETTINGS, \
                                                    PARAMETER_SETTINGS, READ_ME_SET, PARAM_BEST_OPTIONS_THRESHOLD, PARAM_ASSISTANT_TOKENS, print_params

    # ------------------------------------------------------------

    from user_interface_menus._menu_helper import print_global_command_menu, toggle_right_align, exit_interface, toggle_color_output, print_recent_commands

    # ------------------------------------------------------------

    from user_interface_menus.assistant._assistant_menu import assistant_menu

    # ------------------------------------------------------------

    _menu_options = {
        'main': {'description': 'Main Menu', 'menu_caller': main_menu},
        'check': {'description': 'System Status and Diagnostics', 'menu_caller': system_check_menu},
        'diagnostics': {'description': 'Run System Diagnostics', 'menu_caller': lambda self: DIAGNOSTICS(self)},

        'help': {'description': 'Help', 'menu_caller': help_menu},
        'help general': {'description': 'General Information', 'menu_caller': GENERAL_INFORMATION},
        'help ra': {'description': 'Research Assistant Documentation', 'menu_caller': research_assistant_documentation},
        'help dev': {'description': 'Developer Documentation', 'menu_caller': developer_documentation},

        'assistant': {'description': 'PRISM Assistant', 'menu_caller': lambda self: assistant_menu(self)},

        'tasks': {'description': 'Manage System Tasks and R Scripts', 'menu_caller': lambda self: system_task_menu(self)},
        'tasks add': {'description': 'Add New Task', 'menu_caller': lambda self: ADD_TASK(self)},
        'add task': {'description': 'Add New Task', 'menu_caller': lambda self: ADD_TASK(self)},
        'tasks add system' : {'description': 'Add New Task', 'menu_caller': lambda self: ADD_SYSTEM_TASK(self)},
        'add system': {'description': 'Add New System Task', 'menu_caller': lambda self: ADD_SYSTEM_TASK(self)},
        'tasks add rscript': {'description': 'Add New R Script Task', 'menu_caller': lambda self: ADD_R_SCRIPT(self)},
        'add rscript': {'description': 'Add New R Script Task', 'menu_caller': lambda self: ADD_R_SCRIPT(self)},
        'tasks remove': {'description': 'Remove Task', 'menu_caller': lambda self: REMOVE_TASK(self)},
        'remove task': {'description': 'Remove Task', 'menu_caller': lambda self: REMOVE_TASK(self)},
        'tasks execute': {'description': 'Execute Task Now', 'menu_caller': lambda self: EXECUTE_TASK(self)},
        'tasks execute system': {'description': 'Execute System Task Now', 'menu_caller': lambda self: EXECUTE_SYSTEM_TASK(self)},
        'tasks execute rscript': {'description': 'Execute R Script Task Now', 'menu_caller': lambda self: EXECUTE_R_SCRIPT(self)},
        'execute task': {'description': 'Execute Task Now', 'menu_caller': lambda self: EXECUTE_TASK(self)},
        'execute system': {'description': 'Execute System Task Now', 'menu_caller': lambda self: EXECUTE_SYSTEM_TASK(self)},
        'execute rscript': {'description': 'Execute R Script Task Now', 'menu_caller': lambda self: EXECUTE_R_SCRIPT(self)},
        'tasks clear': {'description': 'Clear Task Schedule', 'menu_caller': lambda self: CLEAR_TASKS(self)},
        
        'participants': {'description': 'Manage Participants', 'menu_caller': participant_management_menu},
        'participants add': {'description': 'Add New Participant', 'menu_caller': lambda self: ADD_PARTICIPANT(self)},
        'add participant': {'description': 'Add New Participant', 'menu_caller': lambda self: ADD_PARTICIPANT(self)},
        'participants refresh': {'description': 'Refresh Participants from CSV', 'menu_caller': lambda self: PARTICIPANT_REFRESH(self)},
        'refresh participants': {'description': 'Refresh Participants from CSV', 'menu_caller': lambda self: PARTICIPANT_REFRESH(self)},
        'participants announcement': {'description': 'Send Study Announcement', 'menu_caller': lambda self: PARTICIPANT_ANNOUNCEMENT(self)},
        'announcement': {'description': 'Send Study Announcement', 'menu_caller': lambda self: PARTICIPANT_ANNOUNCEMENT(self)},
        
        'logs': {'description': 'View Logs', 'menu_caller': log_menu},
        'logs transcript': {'description': 'View Today\'s Transcript', 'menu_caller': lambda self: PRINT_TRANSCRIPT(self, 'get_transcript')},
        'transcript': {'description': 'View Today\'s Transcript', 'menu_caller': lambda self: PRINT_TRANSCRIPT(self, 'get_transcript')},
        'transcript log': {'description': 'View Today\'s Transcript', 'menu_caller': lambda self: PRINT_TRANSCRIPT(self, 'get_transcript')},
        'ema log': {'description': 'View EMA Transcript', 'menu_caller': lambda self: PRINT_TRANSCRIPT(self, 'get_ema_log')},
        'logs ema': {'description': 'View EMA Transcript', 'menu_caller': lambda self: PRINT_TRANSCRIPT(self, 'get_ema_log')},
        'logs feedback': {'description': 'View Feedback Survey Log', 'menu_caller': lambda self: PRINT_TRANSCRIPT(self, 'get_feedback_log')},
        'feedback log': {'description': 'View Feedback Survey Log', 'menu_caller': lambda self: PRINT_TRANSCRIPT(self, 'get_feedback_log')},

        'settings': {'description': 'Settings', 'menu_caller': settings_menu},  
        'settings system': {'description': 'System Settings', 'menu_caller': lambda self: SYSTEM_SETTINGS(self)},
        'system settings': {'description': 'System Settings', 'menu_caller': lambda self: SYSTEM_SETTINGS(self)},
        'settings system params': {'description': 'Manage System Parameters (advanced)', 'menu_caller': lambda self: PARAMETER_SETTINGS(self)},
        'params': {'description': 'Manage System Parameters (advanced)', 'menu_caller': lambda self: PARAMETER_SETTINGS(self)},
        'params threshold': {'description': 'Manage similarity tolerance for command suggestions', 'menu_caller': lambda self: PARAM_RELATED_THRESHOLD(self)},
        'params best threshold': {'description': 'Manage similarity tolerance for best command suggestions', 'menu_caller': lambda self: PARAM_BEST_OPTIONS_THRESHOLD(self)},
        'params temperature': {'description': 'Manage model temperature for PRISM Assistant', 'menu_caller': lambda self: PARAM_ASSISTANT_TEMPERATURE(self)},
        'params tokens': {'description': 'Manage max tokens for PRISM Assistant', 'menu_caller': lambda self: PARAM_ASSISTANT_TOKENS(self)},
        'params print': {'description': 'Print current system parameters', 'menu_caller': lambda self: print_params(self)},
        'print params': {'description': 'Print current system parameters', 'menu_caller': lambda self: print_params(self)},

        'settings display': {'description': 'Manage Display settings', 'menu_caller': lambda self: DISPLAY(self)},
        'settings display width': {'description': 'Adjust PRISM window width', 'menu_caller': lambda self: WINDOW_WIDTH_SETTINGS(self)},
        'display': {'description': 'Manage Display settings', 'menu_caller': lambda self: DISPLAY(self)},
        'display width': {'description': 'Adjust PRISM window width', 'menu_caller': lambda self: WINDOW_WIDTH_SETTINGS(self)},
        'display align': {'description': 'Toggle right alignment of menu options', 'menu_caller': toggle_right_align},
        'display color': {'description': 'Toggle color output in terminal', 'menu_caller': toggle_color_output},
        'readme': {'description': 'Display README', 'menu_caller': lambda self: README(self)},
        'readme set': {'description': 'Set README display on startup', 'menu_caller': lambda self: READ_ME_SET(self)},

        'shutdown': {'description': 'Shutdown PRISM', 'menu_caller': shutdown_menu},
        
        'command': {'description': 'Global Command Menu; "command <query>" to search', 'menu_caller': print_global_command_menu},
        'recent': {'description': 'View Recent Commands', 'menu_caller': lambda self: print_recent_commands(self)},
        'exit': {'description': 'Exit PRISM User Interface', 'menu_caller': lambda self: exit_interface(self)},
    }
    return _menu_options