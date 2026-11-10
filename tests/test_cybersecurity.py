import unittest
from pipelines.cybersecurity.build import normalize_kev, extract_cvss


class CybersecurityPipelineTests(unittest.TestCase):
    def test_recent_kev_sorted_and_bounded(self):
        items = [{"cveID": "CVE-2026-0001", "dateAdded": "2026-01-01", "vendorProject": "A"}, {"cveID": "CVE-2026-0002", "dateAdded": "2026-02-01", "vendorProject": "B"}]
        rows = normalize_kev(items, limit=1)
        self.assertEqual(rows[0]["cve"], "CVE-2026-0002")
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]["epss"])

    def test_cvss_v31(self):
        self.assertEqual(extract_cvss({"metrics": {"cvssMetricV31": [{"cvssData": {"baseScore": 8.8}}]}}), 8.8)

    def test_no_cvss_is_unknown(self):
        self.assertIsNone(extract_cvss({}))


if __name__ == "__main__":
    unittest.main()
