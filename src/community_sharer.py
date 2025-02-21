import time
from src.poshmark_constants import PoshmarkConstants
from src.poshmark_driver import PoshmarkDriver


class CommunitySharer(PoshmarkDriver):
    '''
    Share closet items of sellers that poshmark_username follows
    '''
    def __init__(self, poshmark_username, pages, num_items):
        super().__init__(poshmark_username)

        # Number of pages to scroll for each closet
        self.pages = pages

        # Number of items to share for each closet
        self.num_items = num_items

    def scroll_through_all_sellers(self):
        # Get the total number of sellers the user follows
        all_following = self.get_total_count(PoshmarkConstants.Following.follower_count)

        # Calculate how many pages we will need to scroll to get full list of sellers
        pages_to_scroll = all_following // PoshmarkConstants.Following.num_sellers_per_page

        # Scroll to get all sellers user follows
        self.scroll_page(pages_to_scroll)
        time.sleep(3)

    def get_follower_usernames(self):
        '''
        Get the list of seller usernames from the page listing all sellers the user is following
        '''
        follower_elements = self.driver.find_elements_by_xpath(PoshmarkConstants.Following.all_followers)
        return [f.text.lstrip('@') for f in follower_elements]

    def get_seller_usernames(self, num_following):
        '''
        Get a subset of length num_following of the list of
        sellers the user follows
        '''
        # Go to the list of sellers the user follows
        url = PoshmarkConstants.URLs.get_user_following(self.poshmark_username)
        self.driver.get(url)
        time.sleep(3)

        # scroll through paginated list of sellers
        self.scroll_through_all_sellers()

        # Get the full list of sellers the user follows
        sellers = self.get_follower_usernames()

        if num_following == 0 or num_following > len(sellers):
            print(f'Found {len(sellers)} followers.  Sharing closet for all.\m')
        else:
            print(f'Found {len(sellers)} followers.  Of these, selecting {num_following} closets to share.\n')
            sellers = np.random.choice(sellers, num_following, replace=False).tolist()
        return sellers

    def run(self, poshmark_password, num_following):
        '''
        Share self.num_items listings from each closet from
        a list of num_following sellers being followed by the poshmark user login
        '''
        self.login(poshmark_password)
        sellers = self.get_seller_usernames(num_following)
        self.run_driver(sellers)

