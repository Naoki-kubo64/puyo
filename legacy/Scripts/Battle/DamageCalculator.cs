using UnityEngine;

public static class DamageCalculator
{
    public static int CalculateChainDamage(int chainCount, int clearedPuyos, GameConfig config)
    {
        float baseDamage = config.baseDamage;
        float chainMultiplier = config.chainMultiplier;
        
        float damage = baseDamage * clearedPuyos;
        
        if (chainCount > 1)
        {
            float chainBonus = Mathf.Pow(chainMultiplier, chainCount - 1);
            damage *= chainBonus;
        }
        
        return Mathf.RoundToInt(damage);
    }
    
    public static int CalculateColorBonus(int[] colorCounts)
    {
        int colorBonus = 0;
        int colorsUsed = 0;
        
        for (int i = 0; i < colorCounts.Length; i++)
        {
            if (colorCounts[i] > 0)
            {
                colorsUsed++;
                
                if (colorCounts[i] >= 8)
                {
                    colorBonus += 50;
                }
                else if (colorCounts[i] >= 6)
                {
                    colorBonus += 25;
                }
                else if (colorCounts[i] >= 4)
                {
                    colorBonus += 10;
                }
            }
        }
        
        if (colorsUsed >= 4)
        {
            colorBonus += 100;
        }
        else if (colorsUsed >= 3)
        {
            colorBonus += 50;
        }
        
        return colorBonus;
    }
    
    public static int CalculateSpeedBonus(float timeToChain)
    {
        if (timeToChain <= 1f)
        {
            return 50;
        }
        else if (timeToChain <= 2f)
        {
            return 25;
        }
        else if (timeToChain <= 3f)
        {
            return 10;
        }
        
        return 0;
    }
    
    public static ChainResult CalculateFullChainDamage(int chainCount, int clearedPuyos, int[] colorCounts, float chainTime, GameConfig config)
    {
        int baseDamage = CalculateChainDamage(chainCount, clearedPuyos, config);
        int colorBonus = CalculateColorBonus(colorCounts);
        int speedBonus = CalculateSpeedBonus(chainTime);
        
        int totalDamage = baseDamage + colorBonus + speedBonus;
        
        return new ChainResult
        {
            baseDamage = baseDamage,
            colorBonus = colorBonus,
            speedBonus = speedBonus,
            totalDamage = totalDamage,
            chainCount = chainCount,
            clearedPuyos = clearedPuyos,
            chainTime = chainTime
        };
    }
}

[System.Serializable]
public class ChainResult
{
    public int baseDamage;
    public int colorBonus;
    public int speedBonus;
    public int totalDamage;
    public int chainCount;
    public int clearedPuyos;
    public float chainTime;
    
    public string GetDetailString()
    {
        return $"Chain {chainCount}x: {baseDamage} + {colorBonus} + {speedBonus} = {totalDamage} damage";
    }
}