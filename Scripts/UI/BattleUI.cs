using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class BattleUI : MonoBehaviour
{
    [Header("Player UI")]
    public Slider playerHealthBar;
    public TextMeshProUGUI playerHealthText;
    
    [Header("Enemy UI")]
    public Slider enemyHealthBar;
    public TextMeshProUGUI enemyHealthText;
    public TextMeshProUGUI enemyAttackTimer;
    
    [Header("Battle Info")]
    public TextMeshProUGUI chainCountText;
    public TextMeshProUGUI damageText;
    public GameObject damageTextPrefab;
    public Transform damageTextParent;
    
    [Header("Game Info")]
    public TextMeshProUGUI stageText;
    public Button pauseButton;
    
    private BattleManager battleManager;
    
    void Start()
    {
        battleManager = FindFirstObjectByType<BattleManager>();
        
        if (pauseButton != null)
        {
            pauseButton.onClick.AddListener(OnPauseClicked);
        }
        
        if (damageText != null)
        {
            damageText.gameObject.SetActive(false);
        }
    }
    
    public void UpdatePlayerHealth(int currentHP, int maxHP)
    {
        if (playerHealthBar != null)
        {
            playerHealthBar.value = (float)currentHP / maxHP;
        }
        
        if (playerHealthText != null)
        {
            playerHealthText.text = $"{currentHP}/{maxHP}";
        }
    }
    
    public void UpdateEnemyHealth(int currentHP, int maxHP)
    {
        if (enemyHealthBar != null)
        {
            enemyHealthBar.value = (float)currentHP / maxHP;
        }
        
        if (enemyHealthText != null)
        {
            enemyHealthText.text = $"{currentHP}/{maxHP}";
        }
    }
    
    public void UpdateEnemyAttackTimer(float timeRemaining)
    {
        if (enemyAttackTimer != null)
        {
            enemyAttackTimer.text = $"Attack in: {timeRemaining:F1}s";
        }
    }
    
    public void ShowChainInfo(int chainCount, int clearedPuyos)
    {
        if (chainCountText != null)
        {
            chainCountText.text = $"Chain: {chainCount}x";
            chainCountText.gameObject.SetActive(true);
            
            Invoke(nameof(HideChainText), 2f);
        }
    }
    
    private void HideChainText()
    {
        if (chainCountText != null)
        {
            chainCountText.gameObject.SetActive(false);
        }
    }
    
    public void ShowDamage(int damage, bool isPlayerDamage = false)
    {
        if (damageTextPrefab != null && damageTextParent != null)
        {
            GameObject damageObj = Instantiate(damageTextPrefab, damageTextParent);
            TextMeshProUGUI damageTextComp = damageObj.GetComponent<TextMeshProUGUI>();
            
            if (damageTextComp != null)
            {
                damageTextComp.text = $"-{damage}";
                damageTextComp.color = isPlayerDamage ? Color.red : Color.yellow;
                
                StartCoroutine(AnimateDamageText(damageObj));
            }
        }
        else if (damageText != null)
        {
            damageText.text = $"-{damage}";
            damageText.color = isPlayerDamage ? Color.red : Color.yellow;
            damageText.gameObject.SetActive(true);
            
            Invoke(nameof(HideDamageText), 1.5f);
        }
    }
    
    private System.Collections.IEnumerator AnimateDamageText(GameObject damageObj)
    {
        Vector3 startPos = damageObj.transform.position;
        Vector3 endPos = startPos + Vector3.up * 50f;
        
        float duration = 1.5f;
        float elapsed = 0f;
        
        TextMeshProUGUI textComp = damageObj.GetComponent<TextMeshProUGUI>();
        Color startColor = textComp.color;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / duration;
            
            damageObj.transform.position = Vector3.Lerp(startPos, endPos, t);
            
            Color color = startColor;
            color.a = 1f - t;
            textComp.color = color;
            
            yield return null;
        }
        
        Destroy(damageObj);
    }
    
    private void HideDamageText()
    {
        if (damageText != null)
        {
            damageText.gameObject.SetActive(false);
        }
    }
    
    public void UpdateStageInfo(int stageNumber)
    {
        if (stageText != null)
        {
            stageText.text = $"Stage {stageNumber}";
        }
    }
    
    private void OnPauseClicked()
    {
        if (battleManager != null)
        {
            battleManager.PauseBattle();
        }
    }
    
    public void ShowVictoryScreen()
    {
        Debug.Log("Victory!");
    }
    
    public void ShowDefeatScreen()
    {
        Debug.Log("Defeat!");
    }
}