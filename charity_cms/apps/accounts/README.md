# Accounts App

The `accounts` application manages user authentication, profile extension, and user registration flows.

## Concept
CharityOS relies on Django's robust built-in `User` model for core authentication (handling password hashing, sessions, etc.). However, standard Django Users lack fields necessary for our SaaS, such as explicit roles (`admin`, `staff`, `donor`) and phone numbers. 

To solve this, the `accounts` app implements a `UserProfile` model that extends the `User` model via a One-to-One relationship.

## Key Components

### Models
- **`UserProfile`**: Contains `user` (O2O), `role`, `phone_number`, and `profile_picture`.

### Signals (`signals.py`)
- **`create_user_profile`**: Hooked to the `post_save` signal of the `User` model. Whenever a `User` is created, it automatically generates a blank `UserProfile` to ensure database integrity.
- **`save_user_profile`**: Hooked to `post_save` of `User` to save the profile whenever the user is saved.

### Forms (`forms.py`)
- **`CustomUserCreationForm`**: Extends Django's user creation form to capture first name, last name, and email during registration.
- **`UserProfileForm`**: Captures extended profile data.
- **`DonorRegistrationForm`**: A specialized form used on the public landing page. It creates the `User`, the `UserProfile` (forcing role to `donor`), and initializes the `Donor` record in the `donors` app in a single transaction.

### Views (`views.py`)
- **`CustomLoginView`**: Handles login, injects CSS classes for styling, and automatically writes an `AuditLog` entry tracking the IP address upon successful login.
- **`DonorRegistrationView`**: Publicly accessible view for new donors to sign up.
