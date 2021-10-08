import json
from .login import InstaLogin
from .utils import delay


class InstaDataCollector(InstaLogin):
    def __init__(self, username, password):
        super().__init__(username, password)
        self.url = "https://www.instagram.com/explore/tags/{}/?__a=1"
        self.next_url = "https://www.instagram.com/explore/tags/{}/?__a=1&max_id={}"
        self.codes = []
        self.hashtag_code_count = 0
        self.next = False
        self.next_id = ""

    def navigate_to_graphql(self, hash_tag):
        """
            Navigate to the hashtag page to collect posts.
        """
        self.driver.get(self.url.format(hash_tag))
        delay(5)

    def navigate_to_next_page(self, hash_tag):
        """
            proceed to next page, if still posts exists to be collected.
        """
        self.driver.get(self.next_url.format(hash_tag, self.next_id))
        delay(5)

    def get_next_page(self, recent):
        """
            parse data to check if next page is there, if exist get url for that.
        """
        self.next = recent["more_available"]
        if self.next:
            self.next_id = recent["next_max_id"]
        else:
            self.next_id = ""

    def get_codes(self, data):
        """
            parse posts url from the api, if the post is not already liked.
        """
        sections = data["data"]["top"]["sections"]
        sections.extend(data["data"]["recent"]["sections"])
        hashtag = data['data']['name']
        
        medias = []
        for section in sections:
            medias.extend(section["layout_content"]["medias"])

        for media in medias:
            if not media["media"]["has_liked"]:
                code = media["media"]["code"]
                profile_name = media["media"]["user"]["username"]
                self.codes.append({
                    "code": code,
                    "profile_name": profile_name,
                    "hashtag": hashtag
                })
                self.hashtag_code_count += 1

    def process_post_data(self, data):
        """
            collect all url of the posts under hashtag.
        """
        if 'data' in data:
            self.get_next_page(data["data"]["recent"])
            self.get_codes(data)
        else:
            raise Exception('[ERR]: Instagram account is not logged in.')

    def get_post_data(self):
        """
            parse the data from the html body.
        """
        post_data = json.loads(self.driver.find_element_by_xpath("/html/body").text)
        self.process_post_data(post_data)

    def get_post_with_hashtag(self, hash_tag, codes_count):
        """
            steps to collect data from the instagram api with  given hashtag.
        """
        self.hashtag_code_count = 0
        self.navigate_to_graphql(hash_tag)
        self.get_post_data()
        while self.hashtag_code_count <= codes_count and self.next:
            self.navigate_to_next_page(hash_tag)
            self.get_post_data()
            delay(40)
        return {
            "codes": self.codes[:codes_count],
        }


class InstagramPostLiker(InstaLogin):
    def __init__(self, username, password):
        super().__init__(username, password)
        self.post_url = "https://www.instagram.com/p/{}/"

    def navigate_to_post(self, code):
        """
            navigate the post's url.
        """
        self.driver.get(self.post_url.format(code))
        delay(7)

    def can_like(self):
        """
            check whether post can be liked.
        """
        i = 0
        while i < 3:
            try:
                like_icon_color = self.driver.execute_script("return document.querySelector('span.fr66n > button > div > span > svg').getAttribute('color')")
                return not like_icon_color == "#ed4956"
            except:
                delay(2)
                i += 1
        

    def click_heart_icon(self):
        """
            like the post, if it's not already liked.
        """
        if self.can_like():
            self.driver.find_element_by_class_name('fr66n').click()
            delay(2)

    def like_post(self, code):
        """
            steps to navigate to post's url and like the post.
        """
        self.navigate_to_post(code)
        self.click_heart_icon()
        return self.post_url.format(code)
