import pickle
from pathlib import Path

import streamlit_authenticator as stauth

names = ["Nicolas Argota", "Eli Fernandez"]
usernames = ["nargota", "efernandez"]
passwords = ["Corte2023", "Corte2023"]
credentials = {
        "usernames":{
            usernames[0]:{
                "name":names[0],
                "password":passwords[0]
                },
            usernames[1]:{
                "name":names[1],
                "password":passwords[1]
                }            
            }
        }
hashed_passwords = stauth.Hasher(passwords).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)