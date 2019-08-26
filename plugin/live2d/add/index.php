<?php

require '../tools/modelList.php';
require '../tools/modelTextures.php';

$modelList = new modelList();
$modelTextures = new modelTextures();

$modelList = $modelList->get_list();
$modelList = $modelList['models'];

foreach ($modelList as $modelName) {
    if (!is_array($modelName) && file_exists('../model/'.$modelName.'/textures.cache')) {
        
        $textures = $texturesNew = array();
        $modelTexturesList = $modelTextures->get_list($modelName);
        $modelNameTextures = $modelTextures->get_textures($modelName);
        if (is_array($modelTexturesList)) foreach ($modelTexturesList['textures'] as $v) $textures[] = str_replace('\/', '/', json_encode($v));
        if (is_array($modelNameTextures)) foreach ($modelNameTextures as $v) $texturesNew[] = str_replace('\/', '/', json_encode($v));
        
        $texturesDiff = array_diff($texturesNew, $textures);
        if (empty($textures)) continue; elseif (empty($texturesDiff)) {
            echo '<p>'.$modelName.' / textures.cache / No Update.</p>'; 
        } else {
            foreach (array_values(array_unique(array_merge($textures, $texturesNew))) as $v) $texturesMerge[] = json_decode($v, 1);
            file_put_contents('../model/'.$modelName.'/textures.cache', str_replace('\/', '/', json_encode($texturesMerge)));
            echo '<p>'.$modelName.' / textures.cache / Updated.</p>';
        }
        
    }
    elseif (is_array($modelName)) continue;
    elseif ($modelTextures->get_list($modelName)) echo '<p>'.$modelName.' / textures.cache / Created.</p>';
}
