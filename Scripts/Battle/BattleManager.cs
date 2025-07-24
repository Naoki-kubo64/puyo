using UnityEngine;
using System.Collections;

public class BattleManager : MonoBehaviour
{
    [Header("References")]
    public Player player;
    public Enemy enemy;
    public PuzzleManager puzzleManager;
    public BattleUI battleUI;
    public GameConfig config;
    
    [Header("Battle Settings")]
    public int stageNumber = 1;
    
    private bool battleActive = false;
    private bool battlePaused = false;
    private float chainStartTime;
    
    public bool IsBattleActive => battleActive && !battlePaused;
    
    void Start()
    {
        InitializeBattle();
    }
    
    void InitializeBattle()
    {
        if (player == null) player = FindFirstObjectByType<Player>();
        if (enemy == null) enemy = FindFirstObjectByType<Enemy>();
        if (puzzleManager == null) puzzleManager = FindFirstObjectByType<PuzzleManager>();
        if (battleUI == null) battleUI = FindFirstObjectByType<BattleUI>();
        
        SetupEventListeners();
        StartBattle();
    }
    
    void SetupEventListeners()
    {
        if (player != null)
        {
            player.OnHealthChanged += OnPlayerHealthChanged;
            player.OnPlayerDied += OnPlayerDefeated;
        }
        
        if (enemy != null)
        {
            enemy.OnHealthChanged += OnEnemyHealthChanged;
            enemy.OnEnemyDied += OnEnemyDefeated;
            enemy.OnAttack += OnEnemyAttack;
        }
        
        if (puzzleManager != null)
        {
            puzzleManager.OnChainCompleted += OnChainCompleted;
        }
    }
    
    void Update()
    {
        if (!battleActive || battlePaused) return;
        
        if (enemy != null && enemy.IsAlive)
        {
            battleUI?.UpdateEnemyAttackTimer(enemy.AttackTimeRemaining);
        }
    }
    
    public void StartBattle()
    {
        battleActive = true;
        battlePaused = false;
        
        if (player != null && player.maxHP <= 0)
        {
            player.maxHP = config.playerMaxHP;
            player.currentHP = config.playerStartHP;
        }
        
        if (enemy != null)
        {
            SetupEnemyForStage();
            enemy.SetBattleActive(true);
        }
        
        if (puzzleManager != null)
        {
            puzzleManager.ResumeGame();
        }
        
        if (battleUI != null)
        {
            battleUI.UpdateStageInfo(stageNumber);
            OnPlayerHealthChanged(player.currentHP, player.maxHP);
            OnEnemyHealthChanged(enemy.currentHP, enemy.maxHP);
        }
        
        chainStartTime = Time.time;
        
        Debug.Log($"Battle started - Stage {stageNumber}");
    }
    
    void SetupEnemyForStage()
    {
        int enemyHP = Mathf.RoundToInt(100 * (1 + stageNumber * 0.3f));
        int enemyDamage = Mathf.RoundToInt(15 * (1 + stageNumber * 0.2f));
        float attackInterval = Mathf.Max(1.5f, config.enemyAttackInterval - stageNumber * 0.1f);
        string enemyName = $"Enemy Lv.{stageNumber}";
        
        enemy.SetStats(enemyHP, enemyDamage, attackInterval, enemyName);
    }
    
    public void PauseBattle()
    {
        battlePaused = !battlePaused;
        
        if (enemy != null)
        {
            enemy.SetBattleActive(!battlePaused);
        }
        
        if (puzzleManager != null)
        {
            if (battlePaused)
                puzzleManager.StopGame();
            else
                puzzleManager.ResumeGame();
        }
        
        Debug.Log($"Battle {(battlePaused ? "paused" : "resumed")}");
    }
    
    void OnPlayerHealthChanged(int currentHP, int maxHP)
    {
        battleUI?.UpdatePlayerHealth(currentHP, maxHP);
    }
    
    void OnEnemyHealthChanged(int currentHP, int maxHP)
    {
        battleUI?.UpdateEnemyHealth(currentHP, maxHP);
    }
    
    void OnEnemyAttack(int damage)
    {
        if (player != null && battleActive && !battlePaused)
        {
            player.TakeDamage(damage);
            battleUI?.ShowDamage(damage, true);
        }
    }
    
    void OnChainCompleted(int chainCount, int clearedPuyos)
    {
        if (!battleActive || battlePaused) return;
        
        float chainTime = Time.time - chainStartTime;
        chainStartTime = Time.time;
        
        int[] colorCounts = new int[5];
        
        ChainResult result = DamageCalculator.CalculateFullChainDamage(
            chainCount, clearedPuyos, colorCounts, chainTime, config);
        
        if (enemy != null && enemy.IsAlive)
        {
            enemy.TakeDamage(result.totalDamage);
            battleUI?.ShowDamage(result.totalDamage, false);
        }
        
        battleUI?.ShowChainInfo(chainCount, clearedPuyos);
        
        Debug.Log($"Chain completed: {result.GetDetailString()}");
    }
    
    public void OnPlayerDefeated()
    {
        if (!battleActive) return;
        
        battleActive = false;
        
        if (enemy != null)
        {
            enemy.SetBattleActive(false);
        }
        
        if (puzzleManager != null)
        {
            puzzleManager.StopGame();
        }
        
        battleUI?.ShowDefeatScreen();
        
        Debug.Log("Player defeated! Game Over.");
        
        StartCoroutine(HandleGameOver());
    }
    
    public void OnEnemyDefeated()
    {
        if (!battleActive) return;
        
        battleActive = false;
        
        if (puzzleManager != null)
        {
            puzzleManager.StopGame();
        }
        
        battleUI?.ShowVictoryScreen();
        
        Debug.Log($"Stage {stageNumber} cleared!");
        
        StartCoroutine(HandleVictory());
    }
    
    IEnumerator HandleVictory()
    {
        yield return new WaitForSeconds(2f);
        
        Debug.Log("Proceeding to reward selection...");
    }
    
    IEnumerator HandleGameOver()
    {
        yield return new WaitForSeconds(2f);
        
        Debug.Log("Returning to main menu...");
    }
    
    public void NextStage()
    {
        stageNumber++;
        StartBattle();
    }
    
    public void RestartBattle()
    {
        if (player != null)
        {
            player.currentHP = player.maxHP;
        }
        
        StartBattle();
    }
    
    void OnDestroy()
    {
        if (player != null)
        {
            player.OnHealthChanged -= OnPlayerHealthChanged;
            player.OnPlayerDied -= OnPlayerDefeated;
        }
        
        if (enemy != null)
        {
            enemy.OnHealthChanged -= OnEnemyHealthChanged;
            enemy.OnEnemyDied -= OnEnemyDefeated;
            enemy.OnAttack -= OnEnemyAttack;
        }
        
        if (puzzleManager != null)
        {
            puzzleManager.OnChainCompleted -= OnChainCompleted;
        }
    }
}