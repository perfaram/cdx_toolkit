#!/usr/bin/env python

import cdx_toolkit_async
import asyncio

warcinfo = {
    'software': 'pypi_cdx_toolkit_async iter-and-warc example',
    'isPartOf': 'EXAMPLE-COMMONCRAWL',
    'description': 'warc extraction',
    'format': 'WARC file version 1.0',
}

url = 'commoncrawl.org/*'

async def main(url, warcinfo):
    cdx = cdx_toolkit_async.CDXFetcher(source='cc')
    await cdx.prepare()

    writer = cdx_toolkit_async.warc.get_writer('EXAMPLE', 'COMMONCRAWL', warcinfo, warc_version='1.1')

    async for obj in cdx.iter(url, limit=10):
        url = obj['url']
        status = obj['status']
        timestamp = obj['timestamp']

        print('considering extracting url', url, 'timestamp', timestamp)
        if status != '200':
            print(' skipping because status was {}, not 200'.format(status))
            continue

        try:
            record = await obj.fetch_warc_record()
        except RuntimeError:
            print(' skipping capture for RuntimeError 404: %s %s', url, timestamp)
            continue
        writer.write_record(record)

        print(' wrote', url)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    tasks = [
        loop.create_task(main(url, warcinfo)),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
