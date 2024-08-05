Outline of the application:

- A python web application that uses streamlit.
    Streamlit UI:

        -Search Box: Use Streamlit's st.text_input component for the search box and Python's re module to implement the search logic.
        - Use st.checkbox component that can be used for the toggle. Use a variable to track the current mode (search or input).
        -Use Streamlit's st.selectbox component is perfect for the part number dropdown. Populate it with the unique part numbers from your database.
        -Use Streamlit's st.dataframe component can be used to display the table. It provides basic sorting and filtering functionality. Use Streamlit's st.button component to add the reload, export, and double-click functionality.
        -  Use a combination of st.empty and st.write to create custom popups. Use a variable to control the visibility of the popup.

- Uses SQLite as its database so we never loose the data. I should be able to connect to the database using any rdbms from outside the container. 
- Uses docker to conteinerize it so it can be run anywyere .
    The container should be configured so that when it is launched it mounts specific OS folder so it can access files by a process that we'll define later. We'll refer to this as the "LOGS FOLDER". 
    - Create a Dockerfile to build the container. The Dockerfile should include the following:
        - Install Python and Streamlit.
        - Copy your application code.
        - Create a volume to mount the "LOGS FOLDER" from the host machine.

    - Provide the necesary docker run command. Make sure to specify the volume mapping to mount the "LOGS FOLDER".
- Will need to run a Python Processes in the background sometimes when the user decides to:

        -Use Python's multiprocessing module to run the background process. This will prevent the process from blocking the Streamlit UI.
        -The background process will need to handle 7z Extraction,  use the py7zr library to extract files from 7z archives.
        - Use Python's os module to interact with the "LOGS FOLDER" and files.
- Additional Considerations:

        -Error Handling: Implement robust error handling to catch unexpected issues.
        -Security: Implement security measures like input validation and authentication. Also implement basic user handling, a login interface with user and password, verty basic but secure. Use a simple username/password system , do not ise third party authentication service. The app will be run locally on an intranet not in the open internet.
        Testing: Write unit tests to ensure the functionality of your application.Proviode guidance on how to use these unit tests.

Basic functionality of the application:

- It is used to keep track of computer parts by serial number and part number, mostly CPUs, and compressed files related to the parts.

- So far the database must have at least three tables:
    1- A table called LOGS to store information extracted from ".7z" files,whith fields as follows:
            - id 
            - file_name (it should store strings up to 100 characters, sample of a file name "100-000000334_9KC4399M10022_000000_AMD-HC-OSV-A003_LRV_20231020_104543")
            - serial_number var_char not null
            - host_status TEXT nullable
            - csv_file_name var_char nullable
            - csv_file_content TEXT nullable  

    2- A table to store information about the parts being tracked called UNITS, which will be used mostly in the Main section described below,  with fields described below: 
        - id serial autoincrement
        - date_added datetime default current_timestamp
        - date_last_modified datetime default current_timestamp
        - serial_number var_char not null primary key
        - part_number 20 digit var_char
        - datecode 10 digit var_char 
        - country 15 digit var_char
        - composite_snpn 30 digit var_char nullable  

    3- A table called AUDIT to store changes to records to the UNITS table and when the compressed files are processed as described later , with fields described below:
        - id serial autoincrement
        - serial_number var_char not null, indexed
        - date_time datetime default current_timestamp
        - changes TEXT ( stores text with details on the changes made to records on the UNITS table)
    
        


- The app will have three areas or three pages as follows:
    1- The main section, and default, called "Main".
    2- A section to handle compressed files loaded from the os into the databse, we'll call it "LOGS" section.

- The Main section interface page has 2 sections as follows :
    1- A top section we'll call topbar where we have the following in horizontal form :
        -A toggle, similar to iOS toggles, to toggle between search mode or input mode.
           Search mode should be default mode when the web app is loaded.
           When toggled to input mode, the app adds records to the database. When in search mode the app searches the database. 
        - A search box mostly intended to search for a serial number, but also a part number can be searched or a combination of serial number and part number can be ebtered to do a search in the SQLite database. The search box accepts searches for partial serial numbers.
        The search box has to detect whether the user is searching for the following 3 cases:
            I- A serial number, either a full serial or partian, this string can identified if the string does not contain a dash or an underscore. Be mindfull that only alphanumberic characters , undersocre and dash are accepted in the search box.
            II- A part number, this can be identified by a string that contains only a single dash and no underscore.
            III- A special string that contains the serial number and the part number separated by an underscore, here is an example "9KQ5064X20158_100-000000346" , where the first part of the string is the serial number and the second part is the part number. When a special string like this is entered and the focus is lost from the search box the app has to attempt deconstructing the string, leave the serial number part in the search box, try to identify the part number and autoselect it in the part number drop down , if not found 
    

        - A Dropdown where to show all the different part numbers. Should have always a top option and defaulted as "Any". If the toggle is in input mode, and the dropdown is set to "Any" in case it was not set or auto identified, should be set to "100-000000000"; if we're in search mode then when searcing in the database then and the droopdown is ANY then the query should look for any in the part number field.

        - A Search button . This search button changes its legend from "Search" in the default color to "Add" in red color, depending on the mode it's set with the toggle.      
    
    2- A bottom section that displays a table with rows and columns, has basic datatable functionality like sorting, filtering and pagination. Implement basic functionality in this table as follows :
        - Show pagination options, default to latest 10 records.
        - Atthe bottom of the table, could be apart of the table or separate from it whatever is easier to implement and maintain, there should be a section with buttons for options to reload the table so the  web table can be refreshed in case the database table has changed, export the current records being shown in the page to csv, export the whole database table to csv.
        - When a record is double clicked on, a popup window or popup dialog should popup on top to show all the details of the record in a table, where the user could edit the fields or perform other actions based on the data of the record. Here are the actions that could be performed on the record in the popup :
            I- I should be able to select click on a record cell and edit all the editable fields if needed. We need to implement some sort of data log to keep track of all changes to the record after the record was inserted in the table, a log with data like date modified, field modified etc. This , I imagine, has to be a separate database table where the record_id would be used to tie the changes to a record in the main table, so the record_id in the log table should be in a field where it is not unique enforced. 
            II- In this popup there should be another web table where we're going to show a list of records found in the "LOGS" table, only show the log_name field, for this record based on the serial number , we'll call this section "LOG FILES" and we'll define more functionality . Once one of this records is clicked on we will show yet another popup on top to display two other fileds from the selected LOGS table record, which will be two blobs of text. This popup will have a dismiss button to dismiss it and go back to the previous popup.
    
- The LOGS section interface page works as follows:
    1- This is to control a process that runs in the background. The user can launch and stop the process at will , tHe user should have the option to run the process in two ways,  "All files" or "New files only" which is default. WHen the process is started we should show a spinner to the user to wait for the process to finish.   THe process should provide detailed output of its progresss as it runs, start, reading which file, etc... 
        
        THe python process has this functionality:
            The process has to have features so that is not run multiple times, only once at a time.
            The process checks for the mounted "LOGS FOLDER" to access  compressed files with 7z commpression.
            
            THe process , in "New files only" mode, checks for the latest modified file ".7z" , grabs the name of it ignoring the extension and the dot before de extension, so it only grabs the name of the file without extension and the dot. If the filename does not exist then it adds a record in the LOGs table for it. THen it continues for the next file in descending order until it finds a file that is already in the table so then the process is stopped.

            The process, in the "All files" mode, does the same but for all of the ".7z" files in the folder until is finished or stopped byt the user.

            This python process, when it finds a new file that can be added to the database, then also stores a record in the AUDIT table for the serial_number that belongs to the file.
            Here is a sample name for these compressed files : "100-000000334_9KC4399M10022_000000_AMD-HC-OSV-A003_LRV_20231020_104543.7z"  

            This process will deal with the compressed .7z files as follows:
                - create a temp folder
                - copy the file to the temp folder
                - make sure the original compressed file is not affected in any way.
                - Analyze the newly copied file name as follows to determine if its valid and we can obtain the serial number from it as follows:
                    I- Make sure the file name starts with a pattern as "XXX-XXXXXXXXX_*_" where the X represent any character, and the * represents anything but not a null string, what we're looking for is the serial number and it should be contained in between the first two underscores of the file name where we're using the * as pattern. If not a valid file then delete this file and move on to the next file.
                    II- Store the extracted serial number string in a variable, show it in the process output.
                
                If we know the file is valid and we have succsessfully extracted the serial number then :
                    - unzip the file to a subfolder inside to the temp folder
                    - among the uncompressed files in the new subfolder it should search for two files:
                        1- a file called "Host_Status.txt". If found, read the text contents of it to a variable to store in the database.
                        2- a csv file with a name which starts with the serial number followed by an underscore and more charactes after the underscore. If found we store the name of this file and also the contents of this file , since its a csv we need to store the data in a serialized manner to to then store it in the database.
                    - Store the data we have collected to the database, serialnumber , and if available host_status and csv_file_name and csv_file_content to the LOGS database.
                    - delete the files in the sub folder
                    - delete the sub folder
                    - continiue to next file 
                
                - If not more files to process then delete the  temp folder  


- The Settings section interface page has the following:
    1- A section for Information about the SQLite database
        - All Information to be able to connect to the databse, IP, port, user, password, all details needed.
        - Size in disk used by the database.
  
        
    2- A section to show basic Status of the LOGS folder, if it exists, if it is empty or not and how many ".7z" files exists if any, etc...


I want to break down the processes in steps:
Step 1:

Lets begin by settings things up before coding, I would like to start by the creation of the container so we can create the container image that runs a simmple hello world application with streamlit.Once we have a handle of this , like being able to fire up the container and being able to access the webapp in the browser and being able to shut it down and on again and it works fine. Make sure the process includes the mounting an OS folder into the container .  

When I'm satisfied I will let you know when we can move on to SETP 2, which I will define later. Ok ?