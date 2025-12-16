package dal.impl.campaign.skills;

import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.impl.campaign.ids.Stats;

public class CaptainsReliabilityEngineering {
	
	public static float PEAK_TIME_BONUS = 80;
	public static float DEGRADE_REDUCTION_PERCENT = 25f;
	public static float MAX_CR_BONUS = 20;
	
	public static float OVERLOAD_REDUCTION = 20f;
	
	public static float CRITICAL_MALFUNCTION_REDUCTION = 50f;
	public static float MALFUNCTION_REDUCTION = 50f;

	public static class Level1 implements ShipSkillEffect {
		
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getDynamic().getMod(Stats.INDIVIDUAL_SHIP_RECOVERY_MOD).modifyFlat(id, 1000f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getDynamic().getMod(Stats.INDIVIDUAL_SHIP_RECOVERY_MOD).unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "如果该舰在战斗中被击沉，将几乎总是可在战后被打捞并修复。";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level2 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getPeakCRDuration().modifyFlat(id, PEAK_TIME_BONUS);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getPeakCRDuration().unmodifyFlat(id);
		}	
		
		public String getEffectDescription(float level) {
			return "+" + (int)(PEAK_TIME_BONUS) + " 秒峰值时间";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level2B implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getCriticalMalfunctionChance().modifyMult(id, 1f - CRITICAL_MALFUNCTION_REDUCTION / 100f);
			stats.getWeaponMalfunctionChance().modifyMult(id, 1f - MALFUNCTION_REDUCTION / 100f);
			stats.getEngineMalfunctionChance().modifyMult(id, 1f - MALFUNCTION_REDUCTION / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getCriticalMalfunctionChance().unmodify(id);
			stats.getWeaponMalfunctionChance().unmodify(id);
			stats.getEngineMalfunctionChance().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			//return "" + (int)(RECOVERY_RATE_BONUS) + "% faster repairs and CR recovery";
			//return "-" + (int)(CRITICAL_MALFUNCTION_REDUCTION) + "% chance of critical malfunctions when at low combat readiness";
			return "-" + (int)(CRITICAL_MALFUNCTION_REDUCTION) + "% 低战备值时的故障概率";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level3 implements ShipSkillEffect {
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getCRLossPerSecondPercent().modifyMult(id, 1f - DEGRADE_REDUCTION_PERCENT / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getCRLossPerSecondPercent().unmodifyMult(id);
		}	
		
		public String getEffectDescription(float level) {
			return "-" + (int)(DEGRADE_REDUCTION_PERCENT) + "% 峰值时间耗尽后战备值衰减的速度";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}

	public static class Level4 implements ShipSkillEffect {

		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getMaxCombatReadiness().modifyFlat(id, MAX_CR_BONUS * 0.01f, "可靠工程 技能");
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getMaxCombatReadiness().unmodify(id);
		}
		
		public String getEffectDescription(float level) {
			return "+" + (int)(MAX_CR_BONUS) + "% 战备值 (CR) 上限";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
	
	public static class Level5 implements ShipSkillEffect {
		
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			stats.getOverloadTimeMod().modifyMult(id, 1f - OVERLOAD_REDUCTION / 100f);
		}
		
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getOverloadTimeMod().unmodify(id);
		}	
		
		public String getEffectDescription(float level) {
			return "-" + (int)(OVERLOAD_REDUCTION) + "% 过载持续时间";
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.PILOTED_SHIP;
		}
	}
		
}
