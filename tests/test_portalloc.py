import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from portalloc import core


class PortallocTest(unittest.TestCase):
    def test_new_state_shape(self):
        state = core.new_state([[8000, 8002]], 2)
        self.assertEqual(state["ranges"], [[8000, 8002]])
        self.assertEqual(state["quota"], 2)
        self.assertEqual(state["allocated"], {})

    def test_alloc_returns_port(self):
        state = core.new_state([[8000, 8002]], 2)
        port = core.alloc(state, "a", "k1", core.Counter())
        self.assertEqual(port, 8000)
        self.assertIn("8000", state["allocated"])

    def test_free_removes_entry(self):
        state = core.new_state([[8000, 8002]], 2)
        port = core.alloc(state, "a", "k1", core.Counter())
        self.assertTrue(core.free(state, port))
        self.assertNotIn(str(port), state["allocated"])

    def test_free_unknown_port(self):
        state = core.new_state([[8000, 8002]], 2)
        self.assertFalse(core.free(state, 8999))

    def test_status_counts(self):
        state = core.new_state([[8000, 8002]], 2)
        core.alloc(state, "a", "k1", core.Counter())
        self.assertEqual(core.status(state)["allocated"], 1)

    def test_save_load_roundtrip(self):
        import tempfile

        state = core.new_state([[8000, 8002]], 2)
        core.alloc(state, "a", "k1", core.Counter())
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            core.save(state, path)
            back = core.load(path)
            self.assertEqual(back["allocated"], state["allocated"])
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
