from django.test import TestCase, Client
from media_app.models import Channel, Content, File, Group

class ChannelAPITestCase(TestCase):
    def setUp(self):
        # static files
        self.file1 = File.objects.create(file='test_file1')
        self.file2 = File.objects.create(file='test_file2')
    
        # some groups
        self.group1 = Group.objects.create(id=1,name="Group 1")
        self.group2 = Group.objects.create(id=2,name="Group 2")
        
        # static contents
        self.content1 = Content.objects.create(title='Content 1',metadata={}, rating=4.5)
        self.content1.files.add(self.file1)

        self.content2 = Content.objects.create(title='Content 2', metadata={}, rating=3.0)
        self.content2.files.add(self.file2)

        self.content3 = Content.objects.create(title='Content 2', metadata={}, rating=2.0)
        self.content3.files.add(self.file2)

        # test channels
        self.channel_1 = Channel.objects.create(title='Channel 1', language='en')
        self.channel_2 = Channel.objects.create(title='Channel 2', language='fr')

        self.channel_1.contents.add(self.content1,self.content2)
        self.channel_2.groups.add(self.group2)

        self.client = Client()

    def test_get_all_channels_no_group_id(self):
        response = self.client.get('/api/get_all_channels/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['channels']), 2)

    def test_get_all_channels_with_group_id(self):
        response = self.client.get('/api/get_all_channels/?group_id=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['channels']), 1)

    def test_get_single_channel_valid_id(self):
        response = self.client.get(f'/api/get_single_channel/{self.channel_1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Channel 1')

    def test_get_single_channel_invalid_id(self):
        response = self.client.get('/api/get_single_channel/999/')
        self.assertEqual(response.status_code, 404)

    def test_get_subchannels_valid_id(self):
        response = self.client.get(f'/api/get_subchannels/{self.channel_1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['subchannels']), 0)

    def test_get_subchannels_invalid_id(self):
        response = self.client.get('/api/get_subchannels/999/')
        self.assertEqual(response.status_code, 404)

    def test_get_channel_content_valid_id(self):
        response = self.client.get(f'/api/get_channel_content/{self.channel_1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['contents']), 2)

    def test_get_channel_content_invalid_id(self):
        response = self.client.get('/api/get_channel_content/999/')
        self.assertEqual(response.status_code, 404)