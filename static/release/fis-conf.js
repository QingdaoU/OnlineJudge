/**
 * Created by virusdefender on 8/25/15.
 */

fis.match('*.{js,css,png,gif}', {
    useHash: true // 开启 md5 戳
});

fis.config.set(
'roadmap.path',
[{reg:'*.html',isHtmlLike : true}
])
;