
# Luagram


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/irmilad/luagram">
    <img src="https://github.com/IRMilad/luagram/blob/main/.github/logo.jpg?raw=true" alt="Logo" width="350" height="350">
  </a>

  <h3 align="center">luagram</h3>
</div>

## About The Project

luagram is a powerful interface that bridges Lua, Python and TDLib, enabling seamless integration between Lua scripts and the Telegram Database Library ([TDLib](https://github.com/tdlib/td)).

# Features
 - Easy integration of TDLib into Lua projects
 - Flexible configuration options for various use cases
 - Full support for Telegram's rich set of features through Lua


# Installation
You can easily install Luagram using pip. Run the following command to install it:

```
pip install luagram
```

# Getting Started

When you run your script with Luagram, the following entities are automatically available globally in your Lua script:

 - create_new_client
 - Status
 - Params
 - Settings
 - BaseLogger

Below is a demonstration of how to use these globals in your script.


## Create a New Client
To create a new client instance, use the following Lua code:

```lua

    local client = create_new_client{
      name = name, -- The name of the client instance.
      params = Params{
          api_id = 12345678, -- Your Telegram API ID.
          api_hash = 'your_api_hash', -- Your Telegram API hash.
          database_encryption_key = 'your_password', -- Key for encrypting the database.
    
          app_version = '1.0.0', -- Optional: Version of your application.
          device_model = 'your_device_model', -- Optional: Model of the device.
          system_version = 'your_system_version', -- Optional: Operating system version.
          system_language_code = 'en', -- Optional: Language code of the system.
          test_mode = false, -- Optional: Set to true to run in test mode.
          use_secret_chats = true, -- Optional: Enable or disable secret chats.
          use_file_database = true, -- Optional: Use a file-based database.
          use_message_database = true, -- Optional: Use a message database.
          use_chat_info_database = true -- Optional: Use a chat information database.
      },
      settings = Settings{
          verbosity = 1, -- TDLib Logging verbosity level.
          base_logger = BaseLogger{
              path = 'log-%name.log', -- Log file path with dynamic name.
              level = 1, -- Log level.
              max_file_size = 2^20 -- Maximum size of log file (1 MB).
          } -- Optional
      } -- Optional
      queue_put_timeout = 10, -- Optional: Timeout for queue operations.
      updates_queue_size = 1000 -- Optional: Size of the updates queue.
    },
    library_path = 'libtdjson.so' -- Path to the TDLib shared library.
    }
```


## Start the Client
Start the client with the following Lua code:

```lua

    function read(update)
        return io.read() -- Function to handle reading user input.
    end
    
    client.start{
        token = 'your_token', -- Optional: bot token.
        phone = 'your_phone_number' or read, -- Optional: Phone number or a function to read it.
        last_name = 'your_last_name', -- Optional: User's last name.
        first_name = 'your_first_name', -- Optional: User's first name.
        code_callback = read, -- Optional: Function to handle the code input.
        password_callback = read -- Optional: Function to handle password input.
    }

```

## Send a Query
Send a query to TDLib and handle the result:

```lua
    result = client{
        query = {
            ['@type'] = 'getMe' -- The type of query to perform.
        },
        block = false -- Optional: Whether the query should be blocking (default is true).
    }
    
    result = result.wait() -- Wait for the result to be available.
    
    -- Handle result status
    if result.status == Status.OK then
        print(result.update) -- Print the result if successful.
    elseif result.status == Status.ERROR then
        print(result.error) -- Print the error message if there was an error.
    elseif result.status == Status.PENDING then 
        print('pending ...') -- Print a pending message if the query is still processing.
    end
```


## Get Updates
Register handlers for different types of updates:

```lua
    function all_updates(update)
        -- Function to handle all types of updates.
    end 
    
    function new_message(update)
        -- Function to handle new messages.
    end
    
    function new_message_and_new_channel_message(update)
        -- Function to handle both new messages and new channel messages.
    end 
    
    client.get_updates{
        handlers = {
            all_updates, -- Handler for all updates.
            {new_message, {'updateNewMessage'}}, -- Handler for new messages.
            {new_message, {'updateNewMessage', 'updateNewChannelMessage'}} -- Handler for new messages and new channel messages.
        }
    }
```


## Stop the Client
Stop the client with this Lua code:

```lua
  client.stop() -- Stop the client instance and release resources.

```

## Running Your Script
To execute your Lua script with Luagram, use the following command:

```
luagram -n CLIENT_NAME -s SCRIPT_PATH

```
Replace CLIENT_NAME with the name of your client instance and SCRIPT_PATH with the path to your Lua script.

