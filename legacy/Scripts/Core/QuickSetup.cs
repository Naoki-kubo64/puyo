using UnityEngine;
using TMPro;
#if UNITY_EDITOR
using UnityEditor;
#endif

#if UNITY_EDITOR
public class QuickSetup : EditorWindow
{
    [MenuItem("Puyo Rogue/Quick Setup Scene")]
    public static void ShowWindow()
    {
        GetWindow<QuickSetup>("Quick Setup");
    }
    
    void OnGUI()
    {
        GUILayout.Label("Puyo Rogue Quick Setup", EditorStyles.boldLabel);
        
        GUILayout.Space(10);
        
        if (GUILayout.Button("Create All GameObjects"))
        {
            CreateGameObjects();
        }
        
        GUILayout.Space(5);
        
        if (GUILayout.Button("Create GameConfig Asset"))
        {
            CreateGameConfig();
        }
        
        GUILayout.Space(5);
        
        if (GUILayout.Button("Create Puyo Prefab"))
        {
            CreatePuyoPrefab();
        }
        
        GUILayout.Space(5);
        
        if (GUILayout.Button("Create FallingPuyo Prefab"))
        {
            CreateFallingPuyoPrefab();
        }
        
        GUILayout.Space(10);
        
        if (GUILayout.Button("Setup Everything (One Click)"))
        {
            SetupEverything();
        }
        
        GUILayout.Space(10);
        
        GUILayout.Label("Instructions:", EditorStyles.boldLabel);
        GUILayout.Label("1. Click 'Setup Everything' button");
        GUILayout.Label("2. Set Camera position to (3, 6, -10)");
        GUILayout.Label("3. Press Play to test!");
    }
    
    void CreateGameObjects()
    {
        // GameManager
        GameObject gameManager = new GameObject("GameManager");
        gameManager.AddComponent<BattleManager>();
        gameManager.AddComponent<Player>();
        gameManager.AddComponent<Enemy>();
        
        // PuzzleSystem
        GameObject puzzleSystem = new GameObject("PuzzleSystem");
        
        GameObject grid = new GameObject("Grid");
        grid.transform.SetParent(puzzleSystem.transform);
        grid.AddComponent<PuzzleGrid>();
        
        GameObject manager = new GameObject("Manager");
        manager.transform.SetParent(puzzleSystem.transform);
        manager.AddComponent<PuzzleManager>();
        
        // UI Canvas
        GameObject canvasGO = new GameObject("Canvas");
        Canvas canvas = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvasGO.AddComponent<UnityEngine.UI.CanvasScaler>();
        canvasGO.AddComponent<UnityEngine.UI.GraphicRaycaster>();
        canvasGO.AddComponent<BattleUI>();
        
        // UI Elements
        CreateUIElements(canvasGO);
        
        Debug.Log("GameObjects created successfully!");
    }
    
    void CreateUIElements(GameObject canvas)
    {
        // Player Health Bar
        GameObject playerHB = CreateSlider(canvas, "PlayerHealthBar", new Vector2(-200, 200));
        
        // Enemy Health Bar  
        GameObject enemyHB = CreateSlider(canvas, "EnemyHealthBar", new Vector2(200, 200));
        
        // Enemy Timer
        CreateTextMeshPro(canvas, "EnemyTimer", new Vector2(200, 150), "Attack in: 3.0s");
        
        // Chain Info
        CreateTextMeshPro(canvas, "ChainInfo", new Vector2(0, 150), "");
        
        // Damage Text
        CreateTextMeshPro(canvas, "DamageText", new Vector2(0, 0), "");
    }
    
    GameObject CreateSlider(GameObject parent, string name, Vector2 position)
    {
        GameObject sliderGO = new GameObject(name);
        sliderGO.transform.SetParent(parent.transform, false);
        
        RectTransform rect = sliderGO.AddComponent<RectTransform>();
        rect.anchoredPosition = position;
        rect.sizeDelta = new Vector2(200, 20);
        
        UnityEngine.UI.Slider slider = sliderGO.AddComponent<UnityEngine.UI.Slider>();
        slider.value = 1f;
        
        // Background
        GameObject background = new GameObject("Background");
        background.transform.SetParent(sliderGO.transform, false);
        UnityEngine.UI.Image bgImage = background.AddComponent<UnityEngine.UI.Image>();
        bgImage.color = Color.gray;
        RectTransform bgRect = background.GetComponent<RectTransform>();
        bgRect.anchorMin = Vector2.zero;
        bgRect.anchorMax = Vector2.one;
        bgRect.offsetMin = Vector2.zero;
        bgRect.offsetMax = Vector2.zero;
        
        // Fill Area
        GameObject fillArea = new GameObject("Fill Area");
        fillArea.transform.SetParent(sliderGO.transform, false);
        RectTransform fillAreaRect = fillArea.GetComponent<RectTransform>();
        fillAreaRect.anchorMin = Vector2.zero;
        fillAreaRect.anchorMax = Vector2.one;
        fillAreaRect.offsetMin = Vector2.zero;
        fillAreaRect.offsetMax = Vector2.zero;
        
        // Fill
        GameObject fill = new GameObject("Fill");
        fill.transform.SetParent(fillArea.transform, false);
        UnityEngine.UI.Image fillImage = fill.AddComponent<UnityEngine.UI.Image>();
        fillImage.color = Color.green;
        RectTransform fillRect = fill.GetComponent<RectTransform>();
        fillRect.anchorMin = Vector2.zero;
        fillRect.anchorMax = Vector2.one;
        fillRect.offsetMin = Vector2.zero;
        fillRect.offsetMax = Vector2.zero;
        
        slider.fillRect = fillRect;
        
        // Add health text as child
        GameObject healthText = CreateTextMeshPro(sliderGO, "HealthText", Vector2.zero, "100/100");
        RectTransform healthTextRect = healthText.GetComponent<RectTransform>();
        healthTextRect.anchorMin = Vector2.zero;
        healthTextRect.anchorMax = Vector2.one;
        healthTextRect.offsetMin = Vector2.zero;
        healthTextRect.offsetMax = Vector2.zero;
        
        return sliderGO;
    }
    
    GameObject CreateTextMeshPro(GameObject parent, string name, Vector2 position, string text)
    {
        GameObject textGO = new GameObject(name);
        textGO.transform.SetParent(parent.transform, false);
        
        RectTransform rect = textGO.AddComponent<RectTransform>();
        rect.anchoredPosition = position;
        rect.sizeDelta = new Vector2(200, 50);
        
        TextMeshProUGUI textComp = textGO.AddComponent<TextMeshProUGUI>();
        textComp.text = text;
        textComp.fontSize = 16;
        textComp.alignment = TextAlignmentOptions.Center;
        textComp.color = Color.white;
        
        return textGO;
    }
    
    void CreateGameConfig()
    {
        GameConfig config = CreateInstance<GameConfig>();
        
        if (!AssetDatabase.IsValidFolder("Assets/ScriptableObjects"))
            AssetDatabase.CreateFolder("Assets", "ScriptableObjects");
            
        AssetDatabase.CreateAsset(config, "Assets/ScriptableObjects/MainGameConfig.asset");
        AssetDatabase.SaveAssets();
        
        Debug.Log("GameConfig created at Assets/ScriptableObjects/MainGameConfig.asset");
    }
    
    void CreatePuyoPrefab()
    {
        GameObject puyo = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        puyo.name = "Puyo";
        
        // Remove collider
        DestroyImmediate(puyo.GetComponent<SphereCollider>());
        
        if (!AssetDatabase.IsValidFolder("Assets/Prefabs"))
            AssetDatabase.CreateFolder("Assets", "Prefabs");
            
        GameObject prefab = PrefabUtility.SaveAsPrefabAsset(puyo, "Assets/Prefabs/Puyo.prefab");
        DestroyImmediate(puyo);
        
        Debug.Log("Puyo prefab created at Assets/Prefabs/Puyo.prefab");
    }
    
    void CreateFallingPuyoPrefab()
    {
        GameObject fallingPuyo = new GameObject("FallingPuyo");
        fallingPuyo.AddComponent<FallingPuyo>();
        
        if (!AssetDatabase.IsValidFolder("Assets/Prefabs"))
            AssetDatabase.CreateFolder("Assets", "Prefabs");
            
        GameObject prefab = PrefabUtility.SaveAsPrefabAsset(fallingPuyo, "Assets/Prefabs/FallingPuyo.prefab");
        DestroyImmediate(fallingPuyo);
        
        Debug.Log("FallingPuyo prefab created at Assets/Prefabs/FallingPuyo.prefab");
    }
    
    void SetupEverything()
    {
        CreateGameConfig();
        CreatePuyoPrefab();
        CreateFallingPuyoPrefab();
        CreateGameObjects();
        SetupReferences();
        
        Debug.Log("Setup completed! Set Camera position to (3, 6, -10) and press Play!");
    }
    
    void SetupReferences()
    {
        // Find created objects
        GameObject gameManager = GameObject.Find("GameManager");
        GameObject grid = GameObject.Find("Grid");
        GameObject manager = GameObject.Find("Manager");
        GameObject canvas = GameObject.Find("Canvas");
        
        // Load assets
        GameConfig config = AssetDatabase.LoadAssetAtPath<GameConfig>("Assets/ScriptableObjects/MainGameConfig.asset");
        GameObject puyoPrefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Prefabs/Puyo.prefab");
        GameObject fallingPuyoPrefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Prefabs/FallingPuyo.prefab");
        
        // Setup BattleManager
        if (gameManager != null)
        {
            BattleManager battleManager = gameManager.GetComponent<BattleManager>();
            battleManager.player = gameManager.GetComponent<Player>();
            battleManager.enemy = gameManager.GetComponent<Enemy>();
            battleManager.puzzleManager = manager?.GetComponent<PuzzleManager>();
            battleManager.battleUI = canvas?.GetComponent<BattleUI>();
            battleManager.config = config;
        }
        
        // Setup PuzzleGrid
        if (grid != null)
        {
            PuzzleGrid puzzleGrid = grid.GetComponent<PuzzleGrid>();
            puzzleGrid.config = config;
            puzzleGrid.gridParent = grid.transform;
            puzzleGrid.puyoPrefab = puyoPrefab;
        }
        
        // Setup PuzzleManager
        if (manager != null)
        {
            PuzzleManager puzzleManager = manager.GetComponent<PuzzleManager>();
            puzzleManager.grid = grid?.GetComponent<PuzzleGrid>();
            puzzleManager.fallingPuyoPrefab = fallingPuyoPrefab;
            puzzleManager.config = config;
        }
        
        // Setup BattleUI
        if (canvas != null)
        {
            BattleUI battleUI = canvas.GetComponent<BattleUI>();
            battleUI.playerHealthBar = GameObject.Find("PlayerHealthBar")?.GetComponent<UnityEngine.UI.Slider>();
            battleUI.enemyHealthBar = GameObject.Find("EnemyHealthBar")?.GetComponent<UnityEngine.UI.Slider>();
            battleUI.playerHealthText = GameObject.Find("PlayerHealthBar/HealthText")?.GetComponent<TextMeshProUGUI>();
            battleUI.enemyHealthText = GameObject.Find("EnemyHealthBar/HealthText")?.GetComponent<TextMeshProUGUI>();
            battleUI.enemyAttackTimer = GameObject.Find("EnemyTimer")?.GetComponent<TextMeshProUGUI>();
            battleUI.chainCountText = GameObject.Find("ChainInfo")?.GetComponent<TextMeshProUGUI>();
            battleUI.damageText = GameObject.Find("DamageText")?.GetComponent<TextMeshProUGUI>();
        }
        
        Debug.Log("References setup completed!");
    }
}
#endif