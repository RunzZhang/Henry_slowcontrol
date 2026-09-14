import Henry_watchdog_database
instrument = input("Enter the instrument PID: ")
start_date = input("Enter the start date (YYYY-MM-DD): ")
end_date = input("Enter the end date (YYYY-MM-DD): ")

filename='output'+instrument+'.csv'

DB =  Henry_watchdog_database.mydatabase()
DB.select_export_data_datastorage(instrument,start_date,end_date,filename)
print("Done! files is written to ~/Downloads/"+filename)