import os
import requests
import luadata
import concurrent.futures

# Load asset IDs from your Lua file
data = luadata.read("d.lua")  # <- this gives you a Python list of IDs

# Make sure the output folder exists
os.makedirs("assets", exist_ok=True)

headers = {
    "User-Agent": "Roblox/WinInet",
}


cookies = {
    ".ROBLOSECURITY": '_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_CAEaAhADIhwKBGR1aWQSFDE1NzA0MDYxMTc2NjcwNjM2MzA5KAM.jmF1M1WMb4ub13dqxEXK-HjuACXCvBq-Gm1G-iZK2KU9D6HBGfX8KS9p2jIAagTRozD4FHwUIaXvBRSOKPnyxgTAdruIrz8iNE5S0HTzGe6eK3fmtswhu94_Qy4AxfawfEGLzFiWKRo_i_gCfH9tjrFkDPQUUJqrw1rzrOFagE2jlA3YzArODBPezFkkgpc0gtiIKSw5HwFztgeQv8iULxH9QNV0QgSpBV6egN3j5xdLZPAM5ude2d7XSjMIzgj4SYra-5iUV1GuDdWXkMpV4_iRLyz2Z17SfwORXyUIOiR3szv2nHJv0DtgHyec5skA8dCTjipDrf0s8OgOaja0DoVCiRlAfteMx-CCGgy8qECBGHt1x7rYZga2vO7H0NQf2V8sIrzkin8cRxCoAM0BUVO6-nxa_1080Umw3CbupBMRag3wwzMO9QuqWjdHksE0KqWfwrafNVFojtesGavGTclRj_d6D4cKkcXKpBRlpHwH_a1l-q4exvopB7Y35JawFD5NgwbVZLNxng1duPAuYDutUEwyHDX5WlkxbA0lCsZWa0Tf2Dejx5EW76qyz0fC4lWK62upNuUkzSZzAHGzPVmCPKOcE_N0bZZncBQ2qLWZhK3zQmhyJxgcaLvmAn9d2E0yLBIhErDYEhzKmJo65CrIMDpe1xHZJvnOKtLnWEYobI6Az3xgitCfim7U4Hl3S06ZDaJiifJr7r438GUckG8pf09-fSG-0aoL5WlozYAkRrzS3B-H58_svz7m7ur74s9AILKINA2owJtZd372ttj9euA', #Only needed when downloading private files 
}

def download_asset(asset_id):
    url = f"https://assetdelivery.roblox.com/v1/asset/?id={asset_id}"

    try:
        r = requests.get(url, headers=headers, cookies=cookies, timeout=10)

        if r.status_code == 200:
            filename = f"{asset_id}.png"      # you set the extension you want
            path = os.path.join("assets", filename)

            with open(path, "wb") as f:
                f.write(r.content)

            print(f"[OK] {asset_id}")
            pass
        else:
            print(f"[FAIL] {asset_id}: HTTP {r.status_code}")

    except Exception as e:
        print(f"[ERR] {asset_id}: {e}")


# SPEED BOOST: download many at once
MAX_THREADS = 16  # safe + fast
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    executor.map(download_asset, data)
