from openai import OpenAI
import textwrap

client = OpenAI()

def summarize_text(text, chunk_size=4000):
    # Adjust the chunk size if needed
    parts = textwrap.wrap(text, chunk_size)
    
    summaries = []
    for part in parts:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Please, summarize this text: {part}"}
            ]
        )
        if completion.choices:
            # Assuming the first choice is the one we're interested in.
            # Here, we access the text attribute directly.
            summary_content = completion.choices[0].message.content  # Correctly access the text content
            summaries.append(summary_content)
        else:
            summaries.append("Summary not available.")
                
    # Combine all the summaries
    final_summary = " ".join(summaries)
    return final_summary

# Your large text goes here
large_text = """
    hi I'm Ahmed I quit my job in April 2023 when this whole AI stuff started
  to be a a little bit of a craze and I started playing around with chat PT and I
  started freaking out over what can be done with it and that got me into coding about
  a few months ago I started a company called might to help businesses and individuals
  automate their work processes and I'll give you an example of exactly what that
  could look like or mean one of the workflows that I've been working on presently
  is a content generator editor and eventually poster to my Twitter feed and other
  various social media platforms so I can recycle for example YouTube videos that
  I create like this one uh and generate other forms of content for my social media
  platforms automatically so I'll show you how this works so let's run my script over
  here open up the user interface it's very you know basic stuff right now it's just
  for functionality and let's say there's a few videos that I'm interested in writing
  tweets about here using using AI in your automation let's copy this link and post
  this here and five insane openi assistant API examples that's pretty cool let's
  see what these five examples are we're going to write five tweet per uh video Let's
  generate this before I click the generate our current balance just to show you how
  much this costs the current balance right now is $10.35 we're about to extract transcripts
  from two videos one is 6 and2 minutes long one is 7 minutes long we're then going
  to summarize these videos into key talking points we're then going to use these
  key talking points to generate Tweets we're then going to use the tweets generated
  to generate images and then we're going to be able to visualize these suets approve
  them and send them to an approved list for scheduling and posting later on and we're
  also going to be able to reject them and edit them so here's how this looks remember
  this is $10.35 let's go so it starts with extracting the transcript so it extracted
  using AI in your automation unbelievable so this must be this one perfect so the
  transcript has been extracted and now we're going to summarize all of this into
  the basic key talking points it started at 342 we're going to see when this ends
  so now we've generated a summary so what's pretty cool about this is that once your
  system is built it will behave in the way that you want it to be behaving it means
  that the come or the output of the automated Generations will be what you theoretically
  do because you can train it based on your Tweet style based on your tone of voice
  based on your historical data so as we can see here we generated our tweets we generated
  our transcripts so here both transcripts are in the same list that's great we've
  generated a summary for both titles uh our tweets have been generated now it's generating
  the image description for each tweet so now each tweet is being processed and a
  little AI agent is crafting a nice image description prompt and then being fed to
  open AI to create an image and we'll also see this image through the Tweet itself
  so we we've been running for two minutes now right and the video is six and a half
  minutes plus 7 minutes long so that's a total of 13 and a half minutes of just watching
  time to be able to properly summarize this and create content around it the idea
  here is videos that I myself post I would be able to extract that information and
  generate other forms of media automatically with it for example creating articles
  for my website or for my LinkedIn page based on my company data the services I provide
  the audience that I'm trying to Target the tone of voice that I want to use uh we
  can generate images and insert that into the article uh and we can Loop this for
  each key talking point to formulate a full article and now the beauty with the new
  developments of open AI allowing us to input 120,000 words as a prompt so really
  possibilities are endless in the cost customization we're at 3:46 it's been 4 minutes
  that this is running technically you can imagine this being done in the background
  and you're like having coffee or walking around or traveling for example and this
  could be working 24/7 in the background generating tweets based on inputs so this
  is really just the beginning and the idea here really is just to show you how I'm
  someone with zero programming background I don't know python I've never coded before
  but I do understand the inputs and outputs required in my work process and chances
  are probably too and if that's the case you can start becoming a programmer tomorrow
  just clearly identify your modules into uh clearly discernable inputs and a discernable
  output that you're looking for and then the Transformations that need to happen
  in between to create that output so I'll give you an example I want to generate
  a text based on an input if I want to create a summary based on a YouTube transcript
  in this case the input of this module that I've called open AI text generator are
  going to be um a path to a document that that describes the systems context uh a
  file path to the assistant context and the initial prompt uh it's a summary that
  I've extracted in this case it can be used for any kind of context it can be anything
  whether it be an article a news article a YouTube video tweets that could be extracted
  or scraped from Twitter pages automatically I mean the input here is anything and
  then the context you can use to customize really the purpose of this little AI head
  that takes in data and outputs information so here we're finished so if we take
  a look over here all of our tweets have been displayed imagine your social media
  strategy on autopilot autonomous AI can now optimize content for demographics 24/7
  ensuring your messages hits the marks every time social media marketing AI Revolution
  a little Emoji a nice cool image I can reject this I can approve this so if I do
  approve it what's cool is that it removes it from my list of to be approved and
  it puts it into a new new list that has approved tweets on it and the reason why
  I've done that is that afterwards I can manage just this list of approved tweets
  I can schedule them I can then process the images to add little text in the middle
  for example add my logo add a little image of myself like I can create that kind
  of standard a little bit like canva but doing it yourself instead of paying canva
  hundreds of dollars a month you can build it yourself or hire a company to build
  it for you really customized to your needs to be as convenient as possible the idea
  here is that eventually should appear on my phone so every time this will run and
  generate these new tweets for me I'll get a notification on my phone and I can just
  go through it really quickly and they reject approve I can edit so I can click in
  here and be like so cool and then I can click approve and that new text is what's
  now Associated to my approved tweets and here it is we should see so cool written
  so cool it's been updated now this information can be used later on listen if this
  seems a little bit overwhelming to to M group.com is the place for you to go contact
  me Reach Out write to me in the messages comment below we can work together and
  we can help it's no longer expensive to do we currently have a real estate agent
  that we automating his onboarding process yeah just Reach Out reach out and let's
  get started at might we build your technology your way customized to exactly your
  workflow I'll continue dabbling over here and we'll make some more videos to show
  you other workflows that we've automated as we go all all right take care rock and
  roll """

# Assuming the function handles chunking correctly
final_summary = summarize_text(large_text)
print(final_summary)