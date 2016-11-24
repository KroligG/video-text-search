from elasticsearch_dsl import DocType
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.field import InnerObjectWrapper, Nested, String, Integer, Float


class Timestamp(InnerObjectWrapper):
    word = String()
    time = Float()


class YoutubeVideo(DocType):
    title = String()
    duration = String()
    rating = String()
    author = String()
    viewcount = Integer()
    thumb = String()

    transscript = String()
    timestamps = Nested(doc_class=Timestamp)

    class Meta:
        index = 'videos2'

    def save(self, **kwargs):
        # self.lines = len(self.body.split())
        return super(YoutubeVideo, self).save(**kwargs)

    @classmethod
    def build_from_recognition(cls, v, recognition_result):
        video = cls(meta={'id': v.videoid},
                    title=v.title,
                    duration=v.duration,
                    rating=v.rating,
                    author=v.author,
                    viewcount=v.viewcount,
                    thumb=v.thumb)
        video.transscript = '\n'.join((x['transcript'] for x in recognition_result))
        video.timestamps = [{"word": t[0], "time": t[1]} for x in recognition_result for t in x["timestamps"]]

        return video


def init(url):
    connections.create_connection(hosts=[url])
    YoutubeVideo.init()
