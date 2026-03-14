import requests
import time
import os
import threading
import keyboard
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

BASE_URL = "https://hero-sms.com/stubs/handler_api.php"

SERVICE = "wa"

PH_COUNTRY = "4"
CO_COUNTRY = "33"

PH_PRICE = 0.2353
CO_PRICE = 0.294

COUNTRY = PH_COUNTRY
TARGET_PRICE = PH_PRICE

selected_index = 0


def api(action, params=None):

    if params is None:
        params = {}

    params["api_key"] = API_KEY
    params["action"] = action

    try:
        r = requests.get(BASE_URL, params=params, timeout=10)
        return r.text
    except:
        return ""


def get_balance():

    res = api("getBalance")

    if "ACCESS_BALANCE" in res:
        return float(res.split(":")[1])

    return 0


def buy_number():

    params = {
        "service": SERVICE,
        "country": COUNTRY,
        "maxPrice": TARGET_PRICE
    }

    return api("getNumber", params)


def get_status(act_id):

    return api("getStatus", {"id": act_id})


def set_status(act_id, status):

    return api("setStatus", {"id": act_id, "status": status})


def monitor_order(order):

    while True:

        if "otp" in order or order.get("cancel"):
            return

        status = get_status(order["id"])

        if "STATUS_OK" in status:

            otp = status.split(":")[1]

            order["otp"] = otp

            set_status(order["id"], 6)

            return

        time.sleep(0.8)


def cancel_menu(orders):

    global selected_index

    while True:

        if len(orders) == 0:
            time.sleep(1)
            continue

        if keyboard.is_pressed("down"):
            selected_index = (selected_index + 1) % len(orders)
            time.sleep(0.2)

        elif keyboard.is_pressed("up"):
            selected_index = (selected_index - 1) % len(orders)
            time.sleep(0.2)

        elif keyboard.is_pressed("enter"):

            order = orders[selected_index]

            if "otp" not in order and not order.get("cancel"):

                print(f"\nCancel nomor: {order['phone']}")

                set_status(order["id"], 8)

                order["cancel"] = True

            time.sleep(0.3)

        os.system("cls" if os.name == "nt" else "clear")

        print("=== HERO SMS AUTO BUY ===\n")

        for i, order in enumerate(orders):

            pointer = "➜" if i == selected_index else " "

            status = "MENUNGGU"

            if order.get("cancel"):
                status = "CANCELLED"

            if "otp" in order:
                status = "OTP " + order["otp"]

            print(f"{i+1}. {pointer} {order['phone']}  [{status}]")

        print("\n⬆⬇ pilih nomor | ENTER cancel")
        print("Ketik nomor contoh: 1 2 3 | ketik all untuk cancel semua")

        if keyboard.is_pressed("a"):

            time.sleep(0.3)

            cmd = input("\nCancel nomor: ")

            if cmd.lower() == "all":

                for order in orders:
                    if "otp" not in order and not order.get("cancel"):
                        set_status(order["id"], 8)
                        order["cancel"] = True

                print("Semua nomor dibatalkan")

            else:

                try:

                    nums = cmd.split()

                    for n in nums:

                        i = int(n) - 1

                        if i < len(orders):

                            order = orders[i]

                            if "otp" not in order and not order.get("cancel"):

                                set_status(order["id"], 8)

                                order["cancel"] = True

                except:
                    pass

        print("\nTekan A lalu ketik nomor untuk cancel massal")

        time.sleep(0.1)


def main():

    global COUNTRY, TARGET_PRICE

    if not API_KEY:
        print("API KEY tidak ada di .env")
        return

    print("\n=== HERO SMS AUTO BUY ===\n")

    print("1. Philippines")
    print("2. Colombia")

    pilih = input("\nPilih negara: ")

    if pilih == "2":
        COUNTRY = CO_COUNTRY
        TARGET_PRICE = CO_PRICE
        print("\nMode Colombia")
    else:
        COUNTRY = PH_COUNTRY
        TARGET_PRICE = PH_PRICE
        print("\nMode Philippines")

    balance = get_balance()

    print("\nSaldo:", balance)
    print("Target Harga:", TARGET_PRICE)

    qty = int(input("\nJumlah nomor: "))

    orders = []

    threading.Thread(target=cancel_menu, args=(orders,), daemon=True).start()

    print("\nMulai hunting nomor...\n")

    while len(orders) < qty:

        res = buy_number()

        if "ACCESS_NUMBER" in res:

            parts = res.split(":")

            act_id = parts[1]
            phone = parts[2]

            print("Nomor:", phone)

            order = {
                "id": act_id,
                "phone": phone
            }

            orders.append(order)

            threading.Thread(target=monitor_order, args=(order,), daemon=True).start()

        elif "NO_NUMBERS" in res:

            print("Harga kosong... retry")

            time.sleep(2)

        else:

            print("Respon:", res)

            time.sleep(3)

    print("\n=== MENUNGGU OTP ===")

    while True:

        selesai = True

        for order in orders:

            if "otp" not in order and not order.get("cancel"):
                selesai = False

        if selesai:
            break

        time.sleep(1)

    print("\nSemua OTP selesai")


if __name__ == "__main__":
    main()