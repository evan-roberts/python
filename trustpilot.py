from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime as dt
from tqdm import tqdm


def parse_date(date_text):
    try:
        lower_date_text = date_text.lower()
        if "minutes ago" in lower_date_text or "minute ago" in lower_date_text:
            minutes = int(date_text.split()[0]) if date_text.split()[0] != "a" else 1
            return dt.datetime.now() - dt.timedelta(minutes=minutes)
        elif "hours ago" in lower_date_text or "hour ago" in lower_date_text:
            hours = (
                int(date_text.split()[0])
                if date_text.split()[0].lower() not in ["an", "a"]
                else 1
            )
            return dt.datetime.now() - dt.timedelta(hours=hours)
        elif "a day ago" in lower_date_text:
            return dt.datetime.now().date() - dt.timedelta(days=1)
        elif "days ago" in lower_date_text:
            days = int(date_text.split()[0])
            return dt.datetime.now().date() - dt.timedelta(days=days)
        else:
            return dt.datetime.strptime(date_text, "%b %d, %Y").date()
    except ValueError:
        print(f"Unexpected date format: {date_text}")
        return None


# Initialize lists
review_titles = []
review_dates_original = []
review_dates = []
review_ratings = []
review_texts = []
experience_dates = []
page_number = []

# Set Trustpilot page numbers to scrape here
from_page = 1
to_page = 5

for i in tqdm(range(from_page, to_page + 1)):
    response = requests.get(
        f"https://www.trustpilot.com/review/www.getyourguide.com?page={i}"
    )
    web_page = response.text
    soup = BeautifulSoup(web_page, "html.parser")

    for review in tqdm(
        soup.find_all(
            class_="styles_cardWrapper__LcCPA styles_show__HUXRb styles_reviewCard__9HxJJ"
        )
    ):
        # Review titles
        review_title = review.find(
            "h2", {"data-service-review-title-typography": "true"}
        )
        review_titles.append(review_title.getText() if review_title else "")

        # Review dates
        review_date_original = review.select_one(selector="time")
        review_dates_original.append(
            review_date_original.getText() if review_date_original else ""
        )

        # Convert review date texts into Python datetime objects
        review_date_text = (
            review_date_original.getText().replace("Updated ", "")
            if review_date_original
            else ""
        )
        review_date = parse_date(review_date_text)
        review_dates.append(review_date)

        # Review ratings
        review_rating = review.find(
            class_="star-rating_starRating__4rrcf star-rating_medium__iN6Ty"
        )
        review_ratings.append(review_rating.findChild()["alt"] if review_rating else "")

        # Review texts
        review_text = review.find("p", {"data-service-review-text-typography": "true"})
        review_texts.append(review_text.getText() if review_text else "")

        # Experience dates
        experience_date_elem = review.find(
            "p", {"data-service-review-date-of-experience-typography": "true"}
        )
        if experience_date_elem:
            experience_date = experience_date_elem.getText().split(":")[-1].strip()
        else:
            experience_date = "Not provided"
        experience_dates.append(experience_date)

        # Append page number
        page_number.append(i)

# Create final dataframe from lists
df_reviews = pd.DataFrame(
    list(
        zip(
            review_titles,
            review_dates_original,
            review_dates,
            review_ratings,
            review_texts,
            experience_dates,
            page_number,
        )
    ),
    columns=[
        "review_title",
        "review_date_original",
        "review_date",
        "review_rating",
        "review_text",
        "experience_date",
        "page_number",
    ],
)

print(df_reviews.head())
