# 🌐 Cloudflare Dynamic DNS Updater (Windows Tray App)

This Python-based application automatically updates your dynamic IP address with your Cloudflare DNS record. It runs in the Windows system tray, checks for IP changes every 15 minutes, and logs the activities to a `log` file.

## 🚀 Features

- Fully compatible with Cloudflare API
- Updates `A` type DNS records
- Detects IP changes and automatically updates DNS records
- All settings are stored in `config.txt`
- Runs in the Windows system tray with minimal user interaction
- Configurable update interval (default: 15 minutes)

## 🛠️ Requirements

- Python 3.x
- Required libraries:
  - `requests`
  - `pystray`
  - `pillow`

You can install the required libraries by running:
    ```bash
    pip install requests pystray pillow
    ```

## ⚙️ Configuration

On first launch, the program will prompt you for the following settings:

- **API Token**: Cloudflare API token with `DNS Edit` permissions
- **DNS Name**: The full DNS name to be updated (e.g., `sub.domain.com`)
- **Record Type**: DNS record type (default is `A`)
- **TTL**: Time-to-live value for the DNS record (default: 120 seconds)
- **Proxy**: Whether to enable Cloudflare proxy (CDN) (default: no)
- **Update Interval**: How often to check for IP updates (default: 15 minutes)

These settings will be saved in a `config.txt` file.

## 💻 Usage

1. Run the script:

    ```bash
    python cf_ddns_tray.py
    ```

2. The first time the script runs, you will be prompted to enter the required configuration details.
3. The application will minimize to the system tray and update the DNS record every 15 minutes (or the specified interval).
4. The application logs all actions to a `cloudflare_ddns.log` file in the same directory.

## 🖥️ Convert to EXE (Optional)

If you want to convert the script to a Windows executable file, you can use PyInstaller:
```bash
pyinstaller --noconsole --onefile cf_ddns_tray.py
```

This will generate a standalone `.exe` file in the `dist` folder.

## 📝 Log File

The application logs its activities in `cloudflare_ddns.log` for troubleshooting and reference. The log file will include:

- IP address updates
- Success and error messages
- API response errors

## 📄 License

This project is licensed under the GNU v3 License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributions

Contributions are welcome! If you find any bugs, issues, or want to improve this project, feel free to open a pull request. Please ensure that your code follows the project’s style and includes relevant tests.

### How to Contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Make your changes and commit (`git commit -am 'Add new feature'`)
4. Push to your branch (`git push origin feature-branch`)
5. Open a pull request to the `main` branch

## 💬 Support

If you have any questions or need further assistance, feel free to open an issue in the repository, or contact the author.

---

Thank you for using Cloudflare Dynamic DNS Updater! 😄
