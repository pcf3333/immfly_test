from django.test import TestCase
from media_app.models import Channel, Content, File
from django.core.exceptions import ValidationError
from django.core.management import call_command

class ChannelRatingTestCase(TestCase):
    def setUp(self):
        # static files
        self.file1 = File.objects.create(file='test_file1')
        self.file2 = File.objects.create(file='test_file2')
        
        # static contents
        self.content1 = Content.objects.create(title='Content 1',metadata={}, rating=4.5)
        self.content1.files.add(self.file1)

        self.content2 = Content.objects.create(title='Content 2', metadata={}, rating=3.0)
        self.content2.files.add(self.file2)

        self.content3 = Content.objects.create(title='Content 2', metadata={}, rating=2.0)
        self.content3.files.add(self.file2)
        

    def test_channel_rating_with_content(self):
        # Creating a channel and adding contents
        channel = Channel.objects.create(title='Channel', language='English')
        channel.contents.add(self.content1)  # 4.5
        channel.contents.add(self.content2)  # 3.0

        self.assertEqual(channel.calculate_rating(), 3.75)
    

    def test_invalid_channel_no_content_no_children(self):
        with self.assertRaises(ValidationError):
            # try to create a channel with no contents or subchannels
            channel = Channel.objects.create(title='Invalid Channel', language='English')
            channel.save()
    

    def test_invalid_channel_with_subchannels_and_content(self):
        with self.assertRaises(ValidationError):
            # try to create a channel with no contents or subchannels
            channel = Channel.objects.create(title='Invalid Channel', language='English')

            # Add a subchannel
            channel.subchannels.add(Channel.objects.create(title='A Subchannel'))
            
            # try to add a content
            content = Content.objects.create(title='Invalid Content', metadata={}, rating=4.0)
            channel.contents.add(content)
            
            # When saving the object, the clean method will be called and will throw the error
            channel.save()


    def test_channel_rating_without_subchannels(self):
        # Creating a channel (invalid, without saving) with no content or children
        channel = Channel.objects.create(title='Channel', language='Spanish')
       
        self.assertIsNone(channel.calculate_rating())
    
    
    def test_channel_rating_with_subchannels_and_no_content(self):
        # Creating a channel, adding a children
        channel1 = Channel.objects.create(title='Channel 1', language='Spanish')
        channel2 = Channel.objects.create(title='Channel 2', language='Spanish',parent=channel1)

        self.assertIsNone(channel1.calculate_rating())
    

    def test_channel_rating_with_subchannels_and_content(self):
        # Creating a channel, adding a children, adding contents to the children
        channel1 = Channel.objects.create(title='Channel 1', language='Spanish')
        channel2 = Channel.objects.create(title='Channel 2', language='Spanish',parent=channel1)

        channel2.contents.add(self.content2)  # 3.0
        channel2.contents.add(self.content3)  # 2.0
        self.assertEqual(channel1.calculate_rating(), 2.5)


    def test_channel_rating_with_multiple_levels_of_subchannels_with_content(self):
        # create nested subchannels
        channel1 = Channel.objects.create(title='Channel 1', language='Spanish')
        channel2 = Channel.objects.create(title='Channel 2', language='Spanish',parent=channel1)
        channel3 = Channel.objects.create(title='Channel 3', language='Spanish',parent=channel1)
        channel4 = Channel.objects.create(title='Channel 4', language='Spanish',parent=channel2)

        # add content to nested subchannels
        channel3.contents.add(self.content1)  # 4.5
        channel4.contents.add(self.content2)  # 3.0
        channel4.contents.add(self.content3)  # 2.0
 
        # Rating of channel 4 == channel 2 (only child) is (3+2)/2 = 2.5
        # Rating of channel 3 is 4.5
        # Therefore, rating of channel 1 will be (2.5+4.5)/2 = 3.5, which are channels 2 and 3
        self.assertEqual(channel1.calculate_rating(), 3.5)

        
    def test_channel_rating_with_MANY_multiple_levels_of_subchannels_with_content(self):
        # create channels
        channel1 = Channel.objects.create(title='Channel 1', language='Spanish')
        channel2 = Channel.objects.create(title='Channel 2', language='Spanish',parent=channel1)
        channel3 = Channel.objects.create(title='Channel 3', language='Spanish',parent=channel1)
        channel4 = Channel.objects.create(title='Channel 4', language='Spanish',parent=channel2)
        channel5 = Channel.objects.create(title='Channel 5', language='Spanish',parent=channel2)
        channel6 = Channel.objects.create(title='Channel 6', language='Spanish',parent=channel4)
        channel7 = Channel.objects.create(title='Channel 7', language='Spanish',parent=channel5)
        channel8 = Channel.objects.create(title='Channel 8', language='Spanish',parent=channel7)

        # add content to subchannels (the only ones with no children are channel 3,6,8)
        channel3.contents.add(self.content3)  # 2.0

        channel6.contents.add(self.content2)  # 3.0
        channel6.contents.add(self.content1)  # 4.5

        channel8.contents.add(self.content2)  # 3.0
        channel8.contents.add(self.content2)  # 3.0
        channel8.contents.add(self.content3)  # 2.0
        channel8.contents.add(self.content3)  # 2.0

        # calculate rating for some channels
        self.assertEqual(channel8.calculate_rating(), 2.5)  # (3+3+2+2)/4 = 2.5
        self.assertEqual(channel6.calculate_rating(), 3.75)   # (3+4.5)/2 = 3.75
        self.assertEqual(channel3.calculate_rating(), 2.0)  # (2)/1 = 2
        self.assertEqual(channel2.calculate_rating(), 3.125)  # (2.5+3.75)/2 = 3.125
        self.assertEqual(channel1.calculate_rating(), 2.5625)  # (3.125+2)/2 = 2.5625

        # Small extra test, to verify the ".csv" is being exported correctly.
        call_command('calculate_channel_ratings')


    def test_channel_rating_with_single_content(self):
        # Creating a channel and adding contents
        channel = Channel.objects.create(title='Channel', language='English')
        channel.contents.add(self.content1)  # 4.5

        self.assertEqual(channel.calculate_rating(), 4.5)
    

    def test_channel_cache_when_calculate_rating(self):
        # Channels
        channel1 = Channel.objects.create(title='Channel 1', language='Spanish')
        channel2 = Channel.objects.create(title='Channel 2', language='Spanish',parent=channel1)
        channel3 = Channel.objects.create(title='Channel 3', language='Spanish',parent=channel1)    
        channel4 = Channel.objects.create(title='Channel 4', language='Spanish',parent=channel2)    
        
        channel3.contents.add(self.content3)  # 2.0
        channel4.contents.add(self.content1)  # 4.5
        channel4.contents.add(self.content2)  # 3.0

        cache = Channel._ratings_cache
        
        # At this point the cache should be empty
        self.assertIsNone(cache.get(channel1.id))
        self.assertIsNone(cache.get(channel2.id))
        self.assertIsNone(cache.get(channel3.id))
        self.assertIsNone(cache.get(channel4.id))

        # Calculate ratings for channel with contents
        channel4.calculate_rating()

        # Verify that the rating os channel 4 has been cached and the others not
        self.assertEqual(cache.get(channel4.id), 3.75)
        self.assertIsNone(cache.get(channel1.id))
        self.assertIsNone(cache.get(channel2.id))
    
        # When calculating the rating for a top channel, all the children channels should be cached too
        channel1.calculate_rating()

        # Check all chached data
        self.assertEqual(cache.get(channel1.id), 2.875)
        self.assertEqual(cache.get(channel2.id), 3.75)
        self.assertEqual(cache.get(channel3.id), 2.0)
        self.assertEqual(cache.get(channel4.id), 3.75)


    def test_channel_cache_clearing_when_updating_channel_content(self):
        # Channels
        channel1 = Channel.objects.create(title='Channel 1', language='Spanish')
        channel2 = Channel.objects.create(title='Channel 2', language='Spanish',parent=channel1)
        channel3 = Channel.objects.create(title='Channel 3', language='Spanish',parent=channel1)    
        channel4 = Channel.objects.create(title='Channel 4', language='Spanish',parent=channel2)    
        
        channel3.contents.add(self.content3)  # 2.0
        channel4.contents.add(self.content1)  # 4.5
        channel4.contents.add(self.content2)  # 3.0

        cache = Channel._ratings_cache

        # Calculate ratings for parent channel, so all channels are cached
        channel1.calculate_rating()

        # Check all chached data
        self.assertEqual(cache.get(channel1.id), 2.875)
        self.assertEqual(cache.get(channel2.id), 3.75)
        self.assertEqual(cache.get(channel3.id), 2.0)
        self.assertEqual(cache.get(channel4.id), 3.75)
    
        # Changing the content for chanel 4, this should delete channels 4,2,1 from the cahce
        channel4.contents.remove(self.content1)
        channel4.save()

        # Check that the only data in the cache is channel 3
        self.assertIsNone(cache.get(channel1.id))
        self.assertIsNone(cache.get(channel2.id))
        self.assertEqual(cache.get(channel3.id), 2.0)
        self.assertIsNone(cache.get(channel4.id))

        # Calculate ratings for parent channel, so all channels are cached
        channel1.calculate_rating()

        # Now the rating should have been changes in the cahce
        self.assertEqual(cache.get(channel1.id), 2.5)
        self.assertEqual(cache.get(channel2.id), 3.0)
        self.assertEqual(cache.get(channel3.id), 2.0)
        self.assertEqual(cache.get(channel4.id), 3.0)


    def test_channel_cache_clearing_when_updating_content(self):
        # Channels
        channel1 = Channel.objects.create(title='Channel 1', language='Spanish')
        channel2 = Channel.objects.create(title='Channel 2', language='Spanish',parent=channel1)
        channel3 = Channel.objects.create(title='Channel 3', language='Spanish',parent=channel1)    
        channel4 = Channel.objects.create(title='Channel 4', language='Spanish',parent=channel2)    
        
        channel3.contents.add(self.content3)  # 2.0
        channel4.contents.add(self.content1)  # 4.5
        channel4.contents.add(self.content2)  # 3.0

        cache = Channel._ratings_cache

        # Calculate ratings for parent channel, so all channels are cached
        channel1.calculate_rating()
    
        # Modifiyng a content that was added to channel 4
        self.content1.rating = 5.0
        self.content1.save()

        # Check that the only data in the cache is channel 3, all other should be erased
        self.assertIsNone(cache.get(channel1.id))
        self.assertIsNone(cache.get(channel2.id))
        self.assertEqual(cache.get(channel3.id), 2.0)
        self.assertIsNone(cache.get(channel4.id))
    

    def test_channel_cache_clearing_when_updating_channel_relations(self):
        # Channels
        channel1 = Channel.objects.create(title='Channel 1', language='Spanish')
        channel2 = Channel.objects.create(title='Channel 2', language='Spanish',parent=channel1)
        channel3 = Channel.objects.create(title='Channel 3', language='Spanish',parent=channel1)    
        channel4 = Channel.objects.create(title='Channel 4', language='Spanish',parent=channel2)    
        channel5 = Channel.objects.create(title='Channel 5', language='Spanish')    
        
        channel3.contents.add(self.content3)  # 2.0
        channel4.contents.add(self.content1)  # 4.5
        channel4.contents.add(self.content2)  # 3.0
        channel5.contents.add(self.content2)  # 3.0


        cache = Channel._ratings_cache

        # Calculate ratings for parent channel, so all channels are cached
        channel1.calculate_rating()
    
        # Adding a new channel with conent to channel 1
        channel5.parent = channel1
        channel5.save()

        # The only channels with no cached rating should be 1 and 5, other should not be affected
        self.assertIsNone(cache.get(channel1.id))
        self.assertIsNone(cache.get(channel5.id))

        self.assertEqual(cache.get(channel2.id), 3.75)
        self.assertEqual(cache.get(channel3.id), 2.0)
        self.assertEqual(cache.get(channel4.id), 3.75)
    

    # Clearing the cahce after every test and putting the rating back to normal
    def tearDown(self):
        Channel._ratings_cache.clear()
        self.content1.rating = 4.5