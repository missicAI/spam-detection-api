import hashlib
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/raw/SMSSpamCollection"
URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
ZIP_SHA256 = "1587ea43e58e82b14ff1f5425c88e17f8496bfcdb67a583dbff9eefaf9963ce3"
DATA_SHA256 = "7d039a24a6083ed9ef0f806ebad56bbb976e3aeb8de05669173bfdc4996c239d"


def ensure_data(path: Path = DATA_PATH) -> Path:
    if path.exists():
        if hashlib.sha256(path.read_bytes()).hexdigest() != DATA_SHA256:
            raise ValueError("Dữ liệu đã thay đổi; đổi tên tệp hiện có trước khi tải lại bản gốc.")
        return path
    with urlopen(URL, timeout=60) as response:
        archive = response.read(5 * 1024 * 1024)
    if hashlib.sha256(archive).hexdigest() != ZIP_SHA256:
        raise ValueError(
            "Checksum ZIP không khớp bản đã kiểm tra. Kiểm tra nguồn trước khi cập nhật checksum."
        )
    with ZipFile(BytesIO(archive)) as zipped:
        content = zipped.read("SMSSpamCollection")
    if hashlib.sha256(content).hexdigest() != DATA_SHA256:
        raise ValueError("Checksum dữ liệu không hợp lệ.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


if __name__ == "__main__":
    print(ensure_data())
