

class PoshmarkConstants:
    '''
    Constants used for driving the Poshmark site for logging in,
    getting and sharing closet items
    '''
    class URLs:
        login = "https://poshmark.ca/login"

        @staticmethod
        def get_user_closet(username):
            return f'https://poshmark.ca/closet/{username}'

        @staticmethod
        def get_user_available_listings(username):
            return PoshmarkConstants.URLs.get_user_closet(username) + \
                   '?availability=available'

        @staticmethod
        def get_user_following(username):
            return f'https://poshmark.ca/user/{username}/following'

    class Login:
        username_element = "login_form[username_email]"
        password_element = "login_form[password]"

    class Closet:
        share_class = "//div[@class='d--fl ai--c social-action-bar__action social-action-bar__share']"
        share_icon_class = 'share-gray-large'

    class Actions:
        click = "arguments[0].click();"
        scroll = "window.scrollTo(0, document.body.scrollHeight);"
        get_height = "return document.documentElement.scrollHeight"

    class Share:
        internal_share_class = "//a[@class='internal-share__link']"

    class Credentials:
        credentials_path = './credentials.py'

    class Following:
        # Number of sellers listed on each page while scrolling followers
        num_sellers_per_page = 48
        follower_count = "//div[@class='navigation--horizontal__link cursor--pointer navigation--horizontal__link--selected']"
        follower_class = "//p[@class='follow__action__follower caption ellipses tc--lg']"

    class Captcha:
        captcha_div = "//div[@class='d--fl  jc--c g-recaptcha-con']"

