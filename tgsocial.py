# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/
import configparser

# Generate social link tags
def genSocial(config, content):
    loopCount = 0
    socialImage = '../images/'

    socialLinks = [config['BLOG']['twitter'], config['BLOG']['facebook'], config['BLOG']['github'], config['BLOG']['email'], config['BLOG']['keybase'], config['BLOG']['google']]
    socialLinkTags = ['[{TWITTER}]', '[{FACEBOOK}]', '[{GITHUB}]', '[{EMAIL}]', '[{KEYBASE}]', '[{GOOGLE}]']
    for x in socialLinkTags:
        try:
            if socialLinks[loopCount] != '':
                if 'FACEBOOK' in x:
                    socialImage = socialImage + 'facebook'
                elif 'TWITTER' in x:
                    socialImage = socialImage + 'twitter'
                elif 'GITHUB' in x:
                    socialImage = socialImage + 'github'
                elif 'KEYBASE' in x:
                    socialImage = socialImage + 'keybase'
                elif 'GOOGLE' in x:
                    socialImage = socialImage + 'google'
                elif 'EMAIL' in x:
                    socialImage = socialImage + 'email'
                socialImage = socialImage + '.png'

                link = socialLinks[loopCount].replace('\'', '')

                content = content.replace(x, '<a class="socialLink" href="' + socialLinks[loopCount].replace('\'', '') + '"><img src="' + socialImage + '" alt="' + x.replace('[', '').replace(']', '').replace('{', '').replace('}', '') + '"></a>')
            else:
                content = content.replace(x, '')
            socialImage = '../images/'
        except KeyError:
            content = content.replace(x, '')
        loopCount = loopCount + 1
    loopCount = 0
    return content