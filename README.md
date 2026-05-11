# judopass_extractor

This project aims to create an Android app that is capable of extracting data (more info [here](#expected-output)) from the judopass app's Qr code, for use in tournaments or identification.

(This programm is still in beta)

## Prerequisits:
:warning: 
 - I, as the creator, and potential contributors are not to be held liable for any misuse of the provided data.
 - I, as the creator, cannot promise a continuing update schedule.
 - The data stored is **not encrypted** at this point.

**This project has no affiliation with the Judopass app or DokuMe.**

Now to the fun part

If you have feature requests or issues, open an issue [here](https://github.com/JusPetBob/judopass_extractor/issues).
If you want to contribute something, you're more than welcome to look at my messy code.

### Installation & Updates

 1. Visit the [Release tab](https://github.com/JusPetBob/judopass_extractor/releases)
 2. Download the latest .apk file & open it with the installer
 3. If Android asks to scan the file before proceeding, just hit ok and install
 4. You're all set; have fun

#### Building from source 
Either clone this repository: `git clone https://github.com/JusPetBob/judopass_extractor.git` or download the `.zip` in the [Release tab](https://github.com/JusPetBob/judopass_extractor/releases).

**Ubuntu**
Run the following inside judopass_extractor:
```
sudo apt install python3.11 python3.11-venv &&
    python3.11 -m venv .buildozer_venv &&
    source .buildozer_venv/bin/activate &&
    pip install buildozer cython==0.29.33 &&
    buildozer android clean debug
```

If you get an `python3.11 not found` error, run:
```
sudo add-apt-repository ppa:deadsnakes/ppa &&
    sudo apt update
```

**Windows**
If you want to build on Windows you are better off using wsl:
```
wsl --install -d Ubuntu-24.04 && wsl
```
and then following the commands provided for the Ubuntu installation 

## Expected output:
The output location is chosen in the app and will be exported as judopass_export.xlsx

The exported values shown are just a guess of what they could be
<table>
    <tr>
        <td><b>FN</b></td>
        <td><b>Firstname</b></td>
    </tr>
    <tr>
        <td><b>LN</b></td>
        <td><b>Lastname</b></td>
    </tr>
    <tr>
        <td><b>val</b></td>
        <td>shows if the license was valid at the time of scan <b>(generated value: "True"/"False")</b></td>
    </tr>
    <tr>
        <td>iss</td>
        <td>probably refers to the vendor so, it will probably  always be "DokuMe"</td>
    </tr>
    <tr>
        <td>UID</td>
        <td>the user ID from judopass/DokuMe</td>
    </tr>
    <tr>
        <td>NO</td>
        <td>refers to some kind of license</td>
    </tr>
    <tr>
        <td>NO</td>
        <td><i>needs further investigation</i></td>
    </tr>
    <tr>
        <td>ID</td>
        <td><i>needs further investigation</i></td>
    </tr>
    <tr>
        <td>DOB</td>
        <td>Date of birth (JJJJ-MM-DD)</td>
    </tr>
    <tr>
        <td>NAT</td>
        <td>Nationality, <i>though it's a numeric value (52=german)</i></td>
    </tr>
    <tr>
        <td>TM</td>
        <td><i>needs further investigation (for me:"")</i></td>
    </tr>
    <tr>
        <td>LT</td>
        <td><i>needs further investigation</i></td>
    </tr>
    <tr>
        <td>LTN</td>
        <td>probably refers to the app, so it will probably always be "Judopass"</td>
    </tr>
    <tr>
        <td><b>exp</b></td>
        <td>refers to the timestamp of license expiration, used to generate <b>val</b></td>
    </tr>
    <tr>
        <td>LT2</td>
        <td>refers to the rank, but is encoded in some numerical value</td>
    </tr>
    <tr>
        <td>KEY</td>
        <td>probeably some api key (be careful about sharing even if it's exposed)</td>
    </tr>
</table>

If you were expecting any other data, like exact club names, those are probeably only avalabile through the DokuMe api, wich the app is incapable of accessing due to legal reasons.

## Other questions
Is the data secure?
> At the moment all data is stored as a unentcrypted JSON in the Android app storage, so as long as your phone is locked, yes.

Is the data used for something not in my control?
> The app has no way of accessing the internet, and there is no database to save to when data is stored on the device.

What happens on deletion? 
> Deleting stored data will result in an immediate deletion on the local storage and **can not be recovered** if it wasn't exported.

## Todos

 | feature | status |
 | --- | :---: |
 | adding the inline edit functionality | :x: |
 | adding an icon | :x: |
 | **Potential features** |  |
 | if wanted adding csv export | :x: |