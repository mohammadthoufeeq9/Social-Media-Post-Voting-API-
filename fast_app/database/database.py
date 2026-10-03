# import psycopg
# from psycopg.rows import dict_row
# import time

# while True:
#     try:
#         conn=psycopg.connect(host='localhost',database='fastapi',user="postgres",password='Thoufeeq1291',row_factory=dict_row)
#         cursor=conn.connect()
#         print("Database connection is successfull!...")
#     except Exception as error:
#         print("Connecting database is unsuccessfull!....")
#         print("Error:",error)
#         time.sleep(2)# it will try every 2 sec to connect
#-----------------above are for psycopg where we need to write manually sql for retriving data to over cone we use sqlAlchmey we write sql as py code that is converted by psycopg to sql then we get the data___________

from sqlalchemy import engine,text,create_engine
from sqlalchemy.orm import sessionmaker
from fast_app.models.post import Base
DATABASE_URL="postgresql+psycopg://postgres:Thoufeeq1291@localhost:5432/fastapi"
engine = create_engine(DATABASE_URL)
# with engine.connect() as conn:
#     result=conn.execute(text("SELECT 1"))        to check connection
#     print("Database connection successfull!!......")
#     print(result.scalar())


Sessionlocal=sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

def get_db():
    db=Sessionlocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)