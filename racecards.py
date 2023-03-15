from bs4 import BeautifulSoup as bs
from _lib import log, __request__, _filter, compareTimes, stringMatchingPercent
from _selectors import racecard__sections, racecard_horse, racecard_verdict
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from writer import typeWriter

from setting import percent_btwn_web_card1_and_webcard2


class RaceCards:
    def __init__(self, driver) -> None:
        self.driver = driver
        self.write = typeWriter()
        self.url = 'https://www.racingpost.com/racecards/'
        self.life_url = 'https://www.sportinglife.com/racing/racecards'
        self.ScrapRaceCardSections()

    def getVerdictText(self, url):
        log('Getting verdict text....')
        self.driver.get('https://www.sportinglife.com' + url)
        html = bs(self.driver.page_source, 'html.parser')
        text = ""
        verdict_players = ""
        try:
            section = html.select('#verdict')[0]
            text = section.select('p')[0].get_text()
            log('verdict text fetched')
            ol = section.select('li')
            i = 1
            for li in ol:
                ahref = li.select('a')
                verdict_players += f"{ahref[0].get_text()}"
                try:
                    verdict_players += f"=> {ahref[1].get_text()} | "
                except:
                    try:
                        verdict_players += f"=> {li.select('span')[0].get_text()} | "
                    except:
                        verdict_players += ""
                i += 1
            log('verdict player fetched')
            return {'verdict': text, 'verdict players': verdict_players}
        except Exception as e:
            log(f'getVerdictText -> failed {e}', 'error')
        return {'verdict': 'None', 'verdict players': ''}

    def getVerdict(self, card_name, race_time):
        log('getting verdict information...')
        self.driver.get('https://www.sportinglife.com/racing/racecards')
        html = bs(self.driver.page_source, 'html.parser')
        try:
            spans = html.select(racecard_verdict[0])
            i = 1
            for span in spans:
                if stringMatchingPercent(span.get_text(), card_name) > percent_btwn_web_card1_and_webcard2:
                    try:
                        new_selector = f"{racecard_verdict[0]}:nth-child({i})"
                        span = self.driver.find_element(
                            By.CSS_SELECTOR, new_selector)
                        ActionChains(self.driver).move_to_element(
                            span).click().perform()
                        log('waiting for 3 sec....', 'alert')
                        time.sleep(2)
                        html = bs(self.driver.page_source, 'html.parser')
                        section = html.select(racecard_verdict[1])[0]
                        ul = section.select('li')
                        log('comparing...!')
                        for li in ul:
                            timeshort = li.select(racecard_verdict[2])[0]
                            if compareTimes(race_time, _filter(timeshort.get_text())):
                                url = li.select('a')[0].get('href')
                                log('Exact Race Found Successfully!')
                                log(f'Refering to get verdict text... {url}')
                                return self.getVerdictText(url)
                        log('Time comparing failed verdict data is fetched!', 'alert')
                        return {}
                    except Exception as e:
                        log(
                            f'getVerdict after matching percent -> failed {e}', 'error')
                        return {}

                i += 1

        except Exception as e:
            log(f'list races failed -> {e}', 'error')

    def ScrapHorses(self, url):
        horses_list = []
        horse_header = {'date': 'None', 'tv': 'None', 'surface': 'None'}
        html = bs(__request__(url), 'html.parser')
        try:
            log('heading data...')
            header_data = html.select(racecard_horse[0])[0].get_text()
            header_data = header_data.strip()
            header_data = header_data.replace('  ', '')
            header_data = header_data.split('\n')
            header_data = [i for i in header_data if i != '']
            try:
                horse_header['date'] = _filter(header_data[0])
            except Exception as e:
                log(
                    f'header_data failed (date not fetched) -> {e}', __type__='alert')
            try:
                horse_header['tv'] = _filter(header_data[1])
            except Exception as e:
                log(
                    f'header_data failed (tv failed fetching) -> {e}', __type__='alert')
            try:
                horse_header['surface'] = _filter(header_data[2])
            except Exception as e:
                log(
                    f'header_data failed (surface not exist on race) -> {e}', __type__='alert')
        except Exception as e:
            log(f'header setup failed -> {e}', __type__='error')
        try:
            forecast = html.select(racecard_horse[4])[0]
            forecast_spans = forecast.select('span')
            forecast_ = ''
            for span in forecast_spans:
                forecast_ += _filter(span.get_text()) + ' '
        except:
            log('forecast not exist!', 'alert')
            forecast_ = 'None'
        horse_header['forecast'] = _filter(forecast_)
        runnersRow = html.select(racecard_horse[1])[0]
        runners = runnersRow.select(racecard_horse[2])
        for runner in runners:
            horse_data = {'runner name': '', 'runner form': '',
                          'last run': 'not set', 'cdbf': 'None', 'tips': 'None'}
            runner_name = runner.select('.RC-runnerName')[0].get_text()
            last_run = ''
            runner_form = ''
            try:
                runner_form = runner.select(racecard_horse[3])[0].get_text()
                last_run = runner.select(
                    '.RC-runnerStats__lastRun')[0].get_text()
            except:
                pass
            cdbf = 'None'
            try:
                cdbf = runner.select(racecard_horse[6])[0].get_text()
            except:
                pass
            tips = 'None'
            try:
                tips = runner.select(racecard_horse[7])[0].get_text()
            except:
                pass
            horse_data['runner name'] = _filter(runner_name)
            horse_data['runner form'] = _filter(runner_form)
            horse_data['last run'] = _filter(last_run)
            horse_data['cdbf'] = _filter(cdbf)
            horse_data['tips'] = _filter(tips)
            horses_list.append(horse_data)
        return {'horse_header': horse_header, 'horses_list': horses_list}

    def ScrapRaceCardSections(self):
        html = bs(__request__(self.url), 'html.parser')
        cards = html.select(racecard__sections[0])
        race_card = {}
        race_card['card name'] = ""
        race_card['time'] = ""
        race_card['card url text'] = ""
        race_card['number of runners'] = ""
        for card in cards:
            card_name = _filter(card.find(racecard__sections[1]).get_text())
            log('CARD -> ' + card_name)
            card_link = card.select(racecard__sections[2])
            k = 1
            for link in card_link:
                log(f'{card_name} race {k} .....', 'highlight')
                k += 1
                card_url = 'https://www.racingpost.com/' + link.get('href')
                card_time = link.select(racecard__sections[3])[0].get_text()
                card_link_name = link.select(
                    racecard__sections[4])[0].get_text()
                card_runners = link.select(
                    racecard__sections[5])[0].get_text()
                race_card['card name'] = card_name
                race_card['time'] = _filter(card_time)
                race_card['card url text'] = _filter(card_link_name)
                race_card['number of runners'] = _filter(card_runners)
                log('scraping horses...')
                horse_data = self.ScrapHorses(card_url)
                log('scraping verdict...')
                verdict = self.getVerdict(card_name, race_card['time'])
                log('collecting objects...')
                horses_list = horse_data.get('horses_list')
                horses_header = horse_data['horse_header']
                race_card = {**race_card, **verdict, **horses_header}
                race_card['horses_list'] = horses_list
                self.write.onExcel(race_card)
            


if __name__ == '__main__':
    RaceCards()
