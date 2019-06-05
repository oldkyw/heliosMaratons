class Movie:
    URL_BASE = 'https://www.helios.pl'

    def __init__(self, title, link):

        self.title = title
        self.link = self.URL_BASE + link
        self.displays = self.get_displays(self.get_display_links())

    def get_display_links(self):
        # get the links for all displays listed in rezerwuj/kup bilet window
        url = self.link
        soup = request_soup(url)
        links = soup.find_all("a", {"class": "hour-link fancybox-reservation"})

        # if there is many displays in single cinema of given movie
        for i in range(len(links)):
            links[i] = self.URL_BASE + links[i]['href']

        return links

    def get_displays(self, displays_links):

        displays = []
        for link in displays_links:
            soup = request_soup(link)

            #cinema name and date_and_time are written in a list
            display_data = soup.find_all("div", {"class": "description"})
            booking = soup.find("a", {"class": "reservation-function wide"})

            # recover cinema, time, date and link to booking for display
            cinema = display_data[0].text
            time_and_date = display_data[1].text
            time = time_and_date.split()[0]
            date = ' '.join(time_and_date.split()[1:])
            booking_link = booking['href']

            # create display object
            display = Display(date, time, cinema, booking_link)

            # go to booking and seat selection page
            print(display.get_free_seats())
            displays.append(display)

        return displays


class Display:

    def __init__(self, date, time, cinema, link):
        self.date = date
        self.time = time
        self.cinema = cinema
        self.booking_link = link

    def get_free_seats(self):
        from requests_html import HTMLSession
        from bs4 import BeautifulSoup

        url = self.booking_link

        session = HTMLSession()
        print(url)
        resp = session.get(url)

        # support for javascript rendering
        resp.html.render()
        soup = BeautifulSoup(resp.html.html, 'html.parser')

        # even though link is ok and javascript rendering is supported
        # another webpage is displayed. Cannot resolve this error

        print(resp.html.html)
        free_seats = soup.find_all("div", {"class": "seat active "})
        return free_seats

################################################################################


def request_soup(url):

    import requests
    from bs4 import BeautifulSoup

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def get_movies_list(city):

    url = Movie.URL_BASE + '/{}/MaratonyFilmowe/'.format(city)
    soup = request_soup(url)

    movies = soup.find_all("h3", {"class": "movie-title"})
    return movies

################################################################################


if __name__ == '__main__':

    movies = []
    cities = ['57,Warszawa', '42,Gdynia']

    #TODO city to be a feature of display
    for city in cities:

        for x in get_movies_list(city):

            title = x.text
            link = x.find('a')['href']
            movie = Movie(title, link)
            movies.append(movie)

