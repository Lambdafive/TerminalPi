"""
    # Script to call rDesktop endlessly via subprocess.call()
    # User, domain and server are to be modified on a per user basis
"""
import subprocess

user = 'a_user'
domain = 'a_domain'
server = 'a_server'

while True:
    subprocess.call(['rdesktop', '-f', '-d', domain, '-u', user, '-r', 'disk:usb=/media/usb', server])
