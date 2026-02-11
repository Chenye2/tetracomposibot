Clear-Host

$display_mode = 1

# Boucle de 0 à 4
foreach ($mapId in 0..4) {
    Write-Host "Arena: $mapId"
    
    # Boucle sur les positions initiales
    foreach ($initPos in @("True", "False")) {
        py tetracomposibot.py config_Paintwars $mapId $initPos $display_mode
    }
}