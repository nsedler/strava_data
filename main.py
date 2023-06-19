import pickle
import time
import pandas as pd
from stravalib.client import Client


def get_latest_date():
    df = pd.read_csv("data/activities.csv")
    df.sort_values(by="start_date_local", ascending=False, inplace=True)
    return df["start_date_local"][0].split(" ")[0]


client = Client()
MY_STRAVA_CLIENT_ID, MY_STRAVA_CLIENT_SECRET = (
    open("client.secret").read().strip().split(",")
)

print("Client ID and secret read from file")


url = client.authorization_url(
    client_id=MY_STRAVA_CLIENT_ID,
    redirect_uri="localhost:5000/authorization",
    scope=["read_all", "profile:read_all", "activity:read_all"],
)

with open("access_token.pickle", "rb") as f:
    access_token = pickle.load(f)
    if time.time() > access_token["expires_at"]:
        print("Token has expired, will refresh")
        refresh_response = client.refresh_access_token(
            client_id=MY_STRAVA_CLIENT_ID,
            client_secret=MY_STRAVA_CLIENT_SECRET,
            refresh_token=access_token["refresh_token"],
        )
        access_token = refresh_response
        with open("access_token.pickle", "wb") as f:
            pickle.dump(refresh_response, f)
        print("Refreshed token saved to file")
        client.access_token = refresh_response["access_token"]
        client.refresh_token = refresh_response["refresh_token"]
        client.token_expires_at = refresh_response["expires_at"]

    else:
        print(
            "Token still valid, expires at {}".format(
                time.strftime(
                    "%a, %d %b %Y %H:%M:%S %Z",
                    time.localtime(access_token["expires_at"]),
                )
            )
        )
        client.access_token = access_token["access_token"]
        client.refresh_token = access_token["refresh_token"]
        client.token_expires_at = access_token["expires_at"]

print("Latest access token read from file\n\n\n\n")


# Create a function to get latest (most current / recent) activity
# added to data/activities.csv
# activities_list = client.get_activities(after=date)

latest_date = get_latest_date()
activities_list = client.get_activities(after=latest_date)


# a-z order | create new field table with different, better names. ex gear = shoe, maps = polyline etc
fields = [
    "achievement_count",
    "average_cadence",
    "average_heartrate",
    "average_speed",  # currently meters/sec, should be either MM:SS pace or MPH (done in notebook)
    "average_temp",  # currently celcius, change to fareignheight (sp?)
    "average_watts",
    "best_efforts",
    "calories",
    "device_name",
    "distance",  # currently meters, should be miles (done in notebook)
    "elapsed_time",  # currently in seconds, should be HH:MM:SS
    "gear",
    "kilojoules",
    "laps",
    "map",
    "max_heartrate",
    "max_speed",  # currently meters/sec, should be either MM:SS pace or MPH
    "max_watts",
    "moving_time",  # currently in seconds, should be HH:MM:SS
    "name",
    "pr_count",
    "sport_type",
    "start_date_local",
    "suffer_score",
    "type",
    "weighted_average_watts",
]


activity_data = []

for activity in activities_list:
    id = activity.id
    act = client.get_activity(id, True)
    my_dict = act.to_dict()
    list = []
    for field in fields:  # probably best to use a switch statement instead
        cur = my_dict.get(field)

        if cur:
            match field:
                case "gear":
                    list.append(cur["name"])
                case "best_efforts":
                    list.append(len(cur))
                case "laps":
                    list.append(len(cur))
                case "map":
                    list.append(cur["polyline"])

                case _:
                    list.append(cur)
        else:
            list.append("")

    activity_data.append(list)


df = pd.DataFrame(activity_data)

df.to_csv(
    "data/BUactivities1.csv",
)  # backup save incase error appending below

df.to_csv("data/activities.csv", mode="a")
