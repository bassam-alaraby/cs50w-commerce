# Commerce

An eBay-like e-commerce auction platform built with Django as part of Harvard's CS50 Web Programming with Python and JavaScript.

## Features

- User registration and authentication
- Create new auction listings with titles, descriptions, categories, image URLs, and initial prices
- View all active auction listings
- View individual listing details
- Place bids on active listings
- Automatically display the current highest bid
- Close auctions as the listing owner
- Display winning bids and auction winners
- Add comments to auction listings
- Add and remove listings from a personal watchlist
- Browse listings by category
- View personal listings
- View auctions won by the logged-in user
- Manage users, listings, bids, and comments through Django Admin

## Structure

```bash
commerce
├── auctions
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── commerce
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
└── README.md
```

## Pages

### Active Listings

Displays all active auction listings, including their titles, images, initial prices, and current highest bids when available.

Each listing links to its detail page.

### Listing Page

Displays the listing's image, description, creation date, initial price, and current highest bid.

Users can place bids on eligible active listings, add comments, and manage their watchlist.

Listing owners can close their auctions.

When an auction ends, the page displays the winning bid and winner, if any.

### Create Listing

Allows authenticated users to create auction listings by providing a title, description, category, image URL, and initial price.

### Categories

Displays available listing categories and allows users to browse listings belonging to a selected category.

### Watchlist

Displays listings saved by the logged-in user.

Users can add listings to or remove them from their watchlist.

### My Listings

Displays auction listings created by the logged-in user.

### My Wins

Displays auctions won by the logged-in user.

### Login and Registration

Allows users to create an account, log in, and access features that require authentication.

### Django Admin

Provides an administrative interface for managing users, listings, bids, and comments.

## Technical Notes

This project uses Django to handle URL routing, request processing, database operations, authentication, and template rendering.

Auction listings, bids, comments, and users are managed through Django models.

The application determines the current highest bid for each listing and displays the winning bid when an auction is closed.

Django's template system is used to render dynamic pages and generate internal links.

Bootstrap 5 is used for responsive layouts, navigation, forms, buttons, and other UI components, with additional CSS for custom styling.

## Running Locally

Clone the repository:

```bash
git clone https://github.com/bassam-alaraby/cs50w-commerce.git
cd cs50w-commerce
```

Install Django:

```bash
pip install django
```

Apply database migrations:

```bash
python manage.py migrate
```

Create an administrator account:

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

Then visit:

```text
http://127.0.0.1:8000
```

## Technologies

- Python
- Django
- SQLite
- HTML5
- CSS3
- Bootstrap 5
- JavaScript
