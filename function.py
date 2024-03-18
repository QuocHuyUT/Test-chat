import psycopg2 as ps
from azure.communication.identity import *
from azure.communication.chat import *
endpoint = "https://healthmonitoring.asiapacific.communication.azure.com/"
connection_string = "endpoint=https://healthmonitoring.asiapacific.communication.azure.com/;accesskey=DqSzvfVZuJ2/z7atiNAzfm0ntwIwnLav/0AbiSp6ZGEt5erKcfTTazD8vmk9xQWGJ6DOI/SF7WvV97g5uQK4HQ=="
identity_client = CommunicationIdentityClient.from_connection_string(connection_string)

def connect_to_db():
    connectDB = ps.connect(
        host="a-3.postgres.database.azure.com",
        dbname="project",
        user="Project_Health_Care_System",
        password="@healthcare2",
        port=5432
    )
    return connectDB.cursor()

'''Initialise the database'''
# cursor = connect_to_db()
# cursor.execute(
#     """
#     CREATE TABLE account_identity(
#         ID VARCHAR,
#         Display_Name VARCHAR,
#         Thread_ID VARCHAR
#     )
#     """)
# cursor.connection.commit()

#Insert data to database
def insert_into_db(cursor, id_value, display_name_value, thread_id_value):
    cursor.execute(
        """
        INSERT INTO account_identity (ID, Display_Name, Thread_ID)
        VALUES (%s, %s, %s)
        """, 
        (id_value, display_name_value, thread_id_value)
    )
    cursor.connection.commit()

#Get values by display_name
def get_values_by_display_name(cursor, display_name):
    cursor.execute("SELECT * FROM account_identity WHERE Display_Name = %s", (display_name,))
    row = cursor.fetchone()
    if row is not None:
        id_value, display_name_value, thread_id_value = row
        return id_value, display_name_value, thread_id_value
    else:
        return None, None, None


class IdentityManager:
    def __init__(self, connection_string):
        self.identity_client = CommunicationIdentityClient.from_connection_string(connection_string)

    def create_user(self):
        user = self.identity_client.create_user()
        return user  

    def get_token(self, user):
        tokenresponse = self.identity_client.get_token(user, scopes=["chat"])
        return tokenresponse.token

    def create_chat_client(self, token):
        chat_client = ChatClient(endpoint, CommunicationTokenCredential(token))
        return chat_client

    def create_chat_thread_id(self, chat_client, topic):
        create_chat_thread_result = chat_client.create_chat_thread(topic)
        return create_chat_thread_result.chat_thread.id

#Create and add user to db
def create_and_add_user_to_db(cursor, display_name, topic):
    manager = IdentityManager(connection_string)
    user = manager.create_user()
    token = manager.get_token(user)

    chat_client = manager.create_chat_client(token)
    thread_id = manager.create_chat_thread_id(chat_client, topic)

    id_value = user.properties['id']

    insert_into_db(cursor, id_value, display_name, thread_id)

    return id_value, display_name, thread_id

cursor = connect_to_db()
# id_value, display_name_value, thread_id_value = create_and_add_user_to_db(cursor, 'Thien1', 'test topic')
id_value, display_name_value, thread_id_value = get_values_by_display_name(cursor, 'Thien')
print(id_value, display_name_value, thread_id_value)