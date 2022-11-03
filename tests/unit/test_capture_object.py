import pytest
import six

import cdx_toolkit_async

@pytest.mark.asyncio
async def test_capture_object():
    cdx_cc = cdx_toolkit_async.CDXFetcher(source='cc')
    await cdx_cc.prepare()
    cdx_ia = cdx_toolkit_async.CDXFetcher(source='ia')
    await cdx_ia.prepare()
    cdx_only = cdx_toolkit_async.CDXFetcher(source='https://web.archive.org/cdx/search/cdx', loglevel='DEBUG')
    await cdx_only.prepare()

    url = 'example.com'
    kwargs = {'limit': 1}

    got_one = False
    async for obj in cdx_only.iter(url, **kwargs):
        got_one = True
        with pytest.raises(ValueError):
            _ = await obj.content()
    assert got_one, 'found a capture cdx_only'

    for cdx in (cdx_cc, cdx_ia):
        got_one = False
        async for obj in cdx.iter(url, **kwargs):
            got_one = True
            content = await obj.content()
            assert isinstance(content, six.binary_type)
            if len(content) == 0:
                # if the first capture happens to be a revisit, the content length will be zero
                pass
            else:
                assert len(content) > 100, str(obj)

            content2 = await obj.content()
            assert content == content2

            r = await obj.fetch_warc_record()
            r2 = await obj.fetch_warc_record()
            assert r == r2

            stream = await obj.content_stream()
            # we read the stream above, so it's at eof
            more_content = stream.read()
            assert len(more_content) == 0

            text = await obj.text()
            assert isinstance(text, six.string_types)
            text2 = await obj.text()
            assert text == text2

            # some duck-type dict texts on obj
            obj['foo'] = 'asdf'
            assert obj['foo'] == 'asdf'
            assert 'foo' in obj
            del obj['foo']

        assert got_one
