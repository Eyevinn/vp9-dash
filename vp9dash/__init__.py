# Copyright 2017 Eyevinn Technology. All rights reserved
# Use of this source code is governed by a MIT License
# license that can be found in the LICENSE file.
# Author: Jonas Birme (Eyevinn Technology)

import subprocess
import os
import logging
from Queue import Queue
from threading import Thread

logger = logging.getLogger('vp9dash')

class VP9Dash:
    def __init__(self, src, cleanup=True):
        self.src = src
        self.output = "DEFAULT"
        self.cleanup = cleanup
        self.profile = []
        self.profile.append({ 'w': '1920', 'h': '1080', 'b': '2000k', 'fps': 30 })
        self.profile.append({ 'w': '1280', 'h': '720', 'b': '1200k', 'fps': 30 })
        self.profile.append({ 'w': '960', 'h': '540', 'b': '800k', 'fps': 30 })
        self.xq = Queue()
        self.num_worker_threads = 5

    def _transcodeVideo(self, profile):
        logger.debug("Transcoding video to %sx%s" % (profile['w'], profile['h']))
        cmd = [os.path.basename('ffmpeg')]
        inter = str(profile['fps'] * 2)
        cmd.extend(['-i', self.src, '-c:v', 'libvpx-vp9'])
        cmd.extend(['-s', '%sx%s' % (profile['w'], profile['h'])])
        cmd.extend(['-b:v', profile['b'], '-keyint_min', inter, '-g', inter])
        cmd.extend(['-tile-columns', '4', '-frame-parallel', '1'])
        cmd.extend(['-an', '-f', 'webm', '-dash', '1'])
        cmd.append('video_%s_%sx%s_%s.webm' % (self.output, profile['w'], profile['h'], profile['b']))
        runcmd(cmd, 'ffmpeg')

    def _transcodeAudio(self):
        logger.debug("Transcoding audio")
        cmd = [os.path.basename('ffmpeg')]
        cmd.extend(['-i', self.src, '-c:a', 'libvorbis', '-b:a', '128k'])
        cmd.extend(['-vn', '-f', 'webm', '-dash', '1'])
        cmd.append('audio_%s_128k.webm' % self.output)
        runcmd(cmd, 'ffmpeg')

    def _buildDASH(self):
        logger.debug("Building DASH manifest")
        cmd = [os.path.basename('ffmpeg')]
        maps = []
        i = 0
        for profile in self.profile:
            cmd.extend(['-f', 'webm_dash_manifest', '-i', 'video_%s_%sx%s_%s.webm' % (self.output, profile['w'], profile['h'], profile['b'])])
            maps.append(str(i))
            i = i + 1
        vmaps = ",".join(maps)
        cmd.extend(['-f', 'webm_dash_manifest', '-i', 'audio_%s_128k.webm' % self.output])
        maps.append(str(i))
        cmd.extend(['-c', 'copy'])
        for m in maps:
            cmd.extend(['-map', str(m)])
        cmd.extend(['-f', 'webm_dash_manifest'])
        cmd.extend(['-adaptation_sets', '"id=0,streams=%s id=1,streams=%d"' % (vmaps, len(maps) - 1)])
        cmd.extend(['-chunk_start_index', '1'])
        cmd.extend(['-chunk_duration_ms', '2000'])
        cmd.append(self.output + '.mpd')
        runcmd(cmd, 'ffmpeg')

    def _cleanup(self):
        if os.path.exists(self.output + '.wav'):
            os.remove(self.output + '.wav')

    def _transcodeWorker(self):
        while True:
            job = self.xq.get()
            profile = job['profile']
            if not os.path.exists('video_%s_%sx%s_%s.webm' % (self.output, profile['w'], profile['h'], profile['b'])):
                self._transcodeVideo(profile)
            self.xq.task_done()

    def toDASH(self, output):
        self.output = output
        for i in range(self.num_worker_threads):
            t = Thread(target=self._transcodeWorker)
            t.daemon = True
            t.start()
        for p in self.profile:
            self.xq.put({ 'profile': p })
        if not os.path.exists('audio_%s_128k.webm' % self.output):
            self._transcodeAudio()
        self.xq.join()
        self._buildDASH()
        if self.cleanup:
            self._cleanup()



def runcmd(cmd, name):
    logger.debug('COMMAND: %s' % cmd)
    try:
        FNULL = open(os.devnull, 'w')
        if logger.getEffectiveLevel() == logging.DEBUG:
            return subprocess.call(cmd)
        else:
            return subprocess.call(cmd, stdout=FNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        message = "binary tool failed with error %d" % e.returncode
        raise Exception(message)
    except OSError as e:
        raise Exception('Command %s not found, ensure that it is in your path' % name)
