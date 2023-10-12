"""
vidsrc.to extractor
Based on https://github.com/justchokingaround/vidsrc-cli/
"""
import re
import requests

def match_regex(pattern, text):
    """
    Returns a regex match if there is one
    """
    matches = re.findall(pattern, text)
    value = None
    if matches:
        value = matches[0]
    return value

def vidsrc(external_id):
    """
    Gets Vidplay links for a given item (movie or episode)
    """
    base_helper_url = "https://9anime.eltik.net"

    # data_id=$(curl -s "https://vidsrc.to/embed/movie/tt2084970 | sed -nE "s@.*data-id=\"([^\"]*)\".*@\1@p")
    data_id_response = requests.get(f"https://vidsrc.to/embed/movie/{external_id}", timeout=10)
    pattern = r'.*data-id="([^"]*)".*'
    data_id = match_regex(pattern, data_id_response.text)
    # print("Data ID", data_id)
    if not data_id:
        return

    # vidplay_id=$(curl -s "https://vidsrc.to/ajax/embed/episode/${data_id}/sources" | tr '{}' '\n' | sed -nE "s@.*\"id\":\"([^\"]*)\".*\"Vidplay.*@\1@p")
    vidplay_id_response = requests.get(f"https://vidsrc.to/ajax/embed/episode/{data_id}/sources", timeout=10)
    pattern = r'\"id\":\"([^\"]*)\".*\"Vidplay'
    vidplay_id = match_regex(pattern, vidplay_id_response.text)
    # print("Vidplay ID", vidplay_id)
    if not vidplay_id:
        return

    # encrypted_provider_url=$(curl -s "https://vidsrc.to/ajax/embed/source/${vidplay_id}" | sed -nE "s@.*\"url\":\"([^\"]*)\".*@\1@p")
    encrypted_provider_url_response = requests.get(f"https://vidsrc.to/ajax/embed/source/{vidplay_id}", timeout=10)
    pattern = r'\"url\":\"([^\"]*)\"'
    encrypted_provider_url = match_regex(pattern, encrypted_provider_url_response.text)
    # print("Encrypted URL", encrypted_provider_url)
    if not encrypted_provider_url:
        return

    # provider_embed=$(curl -s "$base_helper_url/fmovies-decrypt?query=${encrypted_provider_url}&apikey=jerry" | sed -nE "s@.*\"url\":\"([^\"]*)\".*@\1@p")
    provider_embed_response = requests.get(f"{base_helper_url}/fmovies-decrypt?query={encrypted_provider_url}&apikey=jerry", timeout=10)
    pattern = r'\"url\":\"([^\"]*)\"'
    provider_embed = match_regex(pattern, provider_embed_response.text)
    # print("Provider Embed URL", provider_embed)
    if not provider_embed:
        return

    # tmp=$(printf "%s" "$provider_embed" | sed -nE "s@.*/e/([^\?]*)(\?.*)@\1\t\2@p")
    # provider_query=$(printf "%s" "$tmp" | cut -f1)
    # params=$(printf "%s" "$tmp" | cut -f2)
    pattern = r'.*/e/([^\?]*)(\?.*)'
    matches = re.search(pattern, provider_embed)
    provider_query = None
    params = None
    if matches.lastindex == 2:
        provider_query = matches.group(1)
        params = matches.group(2)
    # print("Provider Query", provider_query)
    # print("Params", params)
    if not provider_query or not params:
        return

    # futoken=$(curl -s "vidstream.pro/futoken")
    futoken = requests.get("https://vidstream.pro/futoken", timeout=10).text
    # print("Futoken", futoken)
    if not futoken:
        return
    
    # raw_url=$(curl -s "$base_helper_url/rawvizcloud?query=${provider_query}&apikey=jerry" -d "query=${provider_query}&futoken=${futoken}" | sed -nE "s@.*\"rawURL\":\"([^\"]*)\".*@\1@p")
    raw_url_response = requests.post(f"{base_helper_url}/rawvizcloud?query={provider_query}&apikey=jerry", data={"query": provider_query, "futoken": futoken}, timeout=10)
    pattern = r'\"rawURL\":\"([^\"]*)\"'
    raw_url = match_regex(pattern, raw_url_response.text)
    # print("Raw URL", raw_url)
    if not raw_url:
        return

    # video_link=$(curl -s "$raw_url${params}" -e "$provider_embed" | sed "s/\\\//g" | sed -nE "s@.*file\":\"([^\"]*)\".*@\1@p")
    video_link_response = requests.get(f"{raw_url}{params}", headers={"Referer": provider_embed}, timeout=10)
    cd_link = re.sub(r'\\/', '/', video_link_response.text)
    pattern = r'\"file\":\"([^\"]*)\"'
    matches = re.search(pattern, cd_link)
    video_link = None
    if matches:
        video_link = matches.group(1)
    # print("Video Link", video_link)
    if not video_link:
        return

    # first_file_url="${cd_link#*\"file\":\"}"
    index = cd_link.find('"file":"')
    if index == -1:
        return
    first_file_url = cd_link[index + len('"file":"'):]

    # first_file_url="${first_file_url%%\"*}"
    index = first_file_url.find('"')
    if index == -1:
        return
    first_file_url = first_file_url[:index]
    # print("First File Url", first_file_url)

    return first_file_url

url = vidsrc("205596")
print(url)
