using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif

#if UNITY_EDITOR
public class QuickMaterialSetup : EditorWindow
{
    [MenuItem("Puyo Rogue/Create Puyo Materials")]
    public static void ShowWindow()
    {
        GetWindow<QuickMaterialSetup>("Material Setup");
    }
    
    void OnGUI()
    {
        GUILayout.Label("Puyo Materials Setup", EditorStyles.boldLabel);
        
        GUILayout.Space(10);
        
        if (GUILayout.Button("Create All Puyo Materials"))
        {
            CreatePuyoMaterials();
        }
        
        GUILayout.Space(5);
        
        if (GUILayout.Button("Update Puyo Prefab with Red Material"))
        {
            UpdatePuyoPrefab();
        }
        
        GUILayout.Space(10);
        
        GUILayout.Label("Instructions:", EditorStyles.boldLabel);
        GUILayout.Label("1. Click 'Create All Puyo Materials'");
        GUILayout.Label("2. Click 'Update Puyo Prefab'");
        GUILayout.Label("3. Now ぷよ will be visible in game!");
    }
    
    void CreatePuyoMaterials()
    {
        if (!AssetDatabase.IsValidFolder("Assets/Materials"))
            AssetDatabase.CreateFolder("Assets", "Materials");
        
        // Create materials for each puyo color
        CreateMaterial("PuyoRed", Color.red);
        CreateMaterial("PuyoBlue", Color.blue);
        CreateMaterial("PuyoGreen", Color.green);
        CreateMaterial("PuyoYellow", Color.yellow);
        CreateMaterial("PuyoPurple", Color.magenta);
        
        Debug.Log("All Puyo materials created successfully!");
    }
    
    void CreateMaterial(string name, Color color)
    {
        Material material = new Material(Shader.Find("Universal Render Pipeline/Lit"));
        material.color = color;
        
        string path = $"Assets/Materials/{name}.mat";
        AssetDatabase.CreateAsset(material, path);
        
        Debug.Log($"Created material: {path}");
    }
    
    void UpdatePuyoPrefab()
    {
        GameObject puyoPrefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Prefabs/Puyo.prefab");
        
        if (puyoPrefab == null)
        {
            Debug.LogError("Puyo prefab not found! Please create it first using Quick Setup.");
            return;
        }
        
        Material redMaterial = AssetDatabase.LoadAssetAtPath<Material>("Assets/Materials/PuyoRed.mat");
        
        if (redMaterial == null)
        {
            Debug.LogError("Red material not found! Please create materials first.");
            return;
        }
        
        // Get the prefab instance to modify
        string prefabPath = AssetDatabase.GetAssetPath(puyoPrefab);
        GameObject prefabInstance = PrefabUtility.LoadPrefabContents(prefabPath);
        
        // Update the material
        Renderer renderer = prefabInstance.GetComponent<Renderer>();
        if (renderer != null)
        {
            renderer.material = redMaterial;
        }
        
        // Save the prefab
        PrefabUtility.SaveAsPrefabAsset(prefabInstance, prefabPath);
        PrefabUtility.UnloadPrefabContents(prefabInstance);
        
        Debug.Log("Puyo prefab updated with red material!");
    }
}
#endif