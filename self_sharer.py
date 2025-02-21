from poshmark_constants import PoshmarkConstants
from poshmark_driver import PoshmarkDriver

class SelfSharer(PoshmarkDriver):
    '''
    Share Poshmark user's own closet items
    '''
    def __init__(self, poshmark_username):
        super().__init__(poshmark_username)

        # Number of items to share for each closet
        self.num_items = 0

        # Number of pages to paginate through in closet
        self.pages = 200

    def get_num_closet_items(self):
        self.go_to_seller_closet(self.poshmark_username)
        return self.get_total_count(PoshmarkConstants.Closet.all_listings)

    def run(self, poshmark_password):
        # Log in and instantiate webdriver
        self.login(poshmark_password)

        # Get the total number of items in seller's closet, to get
        # better idea of how many pages is absolute max
        total_num_items = self.get_num_closet_items()

        # Set number of pages based on 16 items per page
        self.pages = total_num_items // 16

        # scroll through closet
        self.scroll_page(self.pages)

        # Get total number of share icons
        share_icons = self.get_closet_share_icons()

        # Number of items to share = # available items in closet
        self.num_items = len(share_icons)
        print(f'Total available items to share: {self.num_items}')

        self.run_driver([self.poshmark_username])