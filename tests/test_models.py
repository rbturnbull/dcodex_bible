from django.test import TestCase

from dcodex_bible.models import *


def make_verse(book_name, chapter, verse):
    rank = BibleVerse.objects.all().count() + 1
    verse, _ = BibleVerse.objects.update_or_create(
        book=book_names.index(book_name),
        chapter=chapter,
        verse=verse,
        defaults=dict(rank=rank),
    )
    return verse


class BibleVerseTests(TestCase):
    def setUp(self):
        self.romans1_1 = make_verse("Romans", chapter=1, verse=1)
        self.first_corinthians1_17 = make_verse("1 Corinthians", chapter=1, verse=17)

        self.first_corinthians2_passage = []
        for verse in range(9, 20):
            self.first_corinthians2_passage.append(
                make_verse("1 Corinthians", chapter=2, verse=verse)
            )

        self.second_corinthians10_15 = make_verse("2 Corinthians", chapter=10, verse=15)
        self.third_john1_1 = make_verse("3 John", chapter=1, verse=1)

        self.hebrews = []
        for chapter in range(1, 8):
            for verse in range(1, 20):  # Not actually the case. Just for testing
                self.hebrews.append(make_verse("Hebrews", chapter=chapter, verse=verse))
        self.hebrews_ids = {x.id for x in self.hebrews}

        self.acts2_2 = make_verse("Acts", chapter=2, verse=2)
        self.acts1_1 = make_verse("Acts", chapter=1, verse=1)

        self.philippians1_20 = make_verse("Philippians", chapter=1, verse=20)
        self.philippians1_27 = make_verse("Philippians", chapter=1, verse=27)
        self.titus1_15 = make_verse("Titus", chapter=1, verse=15)

        self.first_peter1_1 = make_verse("1 Peter", chapter=1, verse=1)
        self.second_peter2_9 = make_verse("2 Peter", chapter=2, verse=9)

    def test_get_from_string(self):
        self.assertEqual(self.romans1_1.id, BibleVerse.get_from_string("Romans 1:1").id)
        self.assertEqual(self.romans1_1.id, BibleVerse.get_from_string("Ro 1:1").id)
        self.assertEqual(self.romans1_1.id, BibleVerse.get_from_string("Ro1_1").id)
        self.assertEqual(self.romans1_1.id, BibleVerse.get_from_string("ro1-1").id)
        self.assertEqual(self.romans1_1.id, BibleVerse.get_from_string("Rom1.1").id)
        self.assertEqual(self.romans1_1.id, BibleVerse.get_from_string("Romans 1").id)
        self.assertEqual(self.romans1_1.id, BibleVerse.get_from_string("Ro").id)

        self.assertEqual(
            self.second_corinthians10_15.id,
            BibleVerse.get_from_string("2 Corinthians 10:15").id,
        )
        self.assertEqual(
            self.second_corinthians10_15.id,
            BibleVerse.get_from_string("2 Cor 10:15").id,
        )
        self.assertEqual(
            self.second_corinthians10_15.id, BibleVerse.get_from_string("2Cor10:15").id
        )
        self.assertEqual(
            self.second_corinthians10_15.id,
            BibleVerse.get_from_string("2Corinth10-15").id,
        )

        self.assertEqual(self.third_john1_1.id, BibleVerse.get_from_string("3Jn1:1").id)
        self.assertEqual(self.third_john1_1.id, BibleVerse.get_from_string("3Jn1").id)
        self.assertEqual(self.acts2_2.id, BibleVerse.get_from_string("Ac 2.2").id)
        self.assertEqual(self.acts1_1.id, BibleVerse.get_from_string("Ac 1.1").id)
        self.assertEqual(
            self.philippians1_20.id, BibleVerse.get_from_string("Php 1.20").id
        )
        self.assertEqual(
            self.philippians1_27.id, BibleVerse.get_from_string("Php 1.27").id
        )
        self.assertEqual(self.titus1_15.id, BibleVerse.get_from_string("Tt 1.15").id)
        self.assertEqual(
            self.first_peter1_1.id, BibleVerse.get_from_string("1Pt 1.1").id
        )
        self.assertEqual(
            self.second_peter2_9.id, BibleVerse.get_from_string("2Pt 2.9").id
        )
        self.assertEqual(
            self.philippians1_20.id, BibleVerse.get_from_string("Phil 1.20").id
        )

    def test_components_from_verse_ref(self):
        self.assertEqual((46, 1, 17), components_from_verse_ref("1 Corinthians 1:17"))
        self.assertEqual((46, 2, 9), components_from_verse_ref("1 Co 2:9"))
        self.assertEqual((44, 1, 1), components_from_verse_ref("Ac 1.1"))

    def test_get_verses_from_string(self):
        self.assertEqual(
            [self.first_corinthians1_17.id],
            [x.id for x in BibleVerse.get_verses_from_string("1 Corinthians 1:17")],
        )
        self.assertEqual(
            [self.first_corinthians1_17.id]
            + [x.id for x in self.first_corinthians2_passage],
            [x.id for x in BibleVerse.get_verses_from_string("1 Co 1:17; 2:9–19")],
        )
        hebrews_verses = BibleVerse.get_verses_from_string(
            "Heb 1:17–22; 2:9–12,14; 3:1–3,5–6; 4:3–5:5,7–8; 6:5–9,11–18; 7:3–6,10–14"
        )
        hebrews_verse_ids = {x.id for x in hebrews_verses}
        self.assertEqual(59, len(hebrews_verse_ids))
        self.assertTrue(hebrews_verse_ids.issubset(self.hebrews_ids))
        self.assertEqual(
            [self.acts1_1.id],
            [x.id for x in BibleVerse.get_verses_from_string("Ac 1.1")],
        )
        self.assertEqual(
            [self.acts1_1.id, self.acts2_2.id],
            [x.id for x in BibleVerse.get_verses_from_string("Ac 1.1; 2:2")],
        )
        self.assertEqual(
            [self.philippians1_20.id, self.philippians1_27.id],
            [x.id for x in BibleVerse.get_verses_from_string("Phil 1:20,27")],
        )
