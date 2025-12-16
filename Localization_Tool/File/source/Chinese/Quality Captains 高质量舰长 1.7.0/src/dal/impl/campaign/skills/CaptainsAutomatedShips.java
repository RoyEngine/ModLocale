package dal.impl.campaign.skills;

import java.awt.Color;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.campaign.FleetDataAPI;
import com.fs.starfarer.api.characters.CharacterStatsSkillEffect;
import com.fs.starfarer.api.characters.DescriptionSkillEffect;
import com.fs.starfarer.api.characters.FleetTotalItem;
import com.fs.starfarer.api.characters.FleetTotalSource;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI;
import com.fs.starfarer.api.characters.ShipSkillEffect;
import com.fs.starfarer.api.characters.SkillSpecAPI;
import com.fs.starfarer.api.characters.LevelBasedEffect.ScopeDescription;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;
import com.fs.starfarer.api.impl.campaign.AICoreOfficerPluginImpl;
import com.fs.starfarer.api.impl.campaign.ids.Skills;
import com.fs.starfarer.api.impl.campaign.ids.Strings;
import com.fs.starfarer.api.impl.campaign.ids.Tags;
import com.fs.starfarer.api.impl.campaign.skills.AutomatedShips;
import com.fs.starfarer.api.impl.campaign.skills.BaseSkillEffectDescription;
import com.fs.starfarer.api.impl.hullmods.Automated;
import com.fs.starfarer.api.ui.TooltipMakerAPI;
import com.fs.starfarer.api.util.Misc;

public class CaptainsAutomatedShips extends AutomatedShips {
	
	public static boolean USE_AUTOMATED_LIMITS = true;
	public static boolean USE_AUTOMATED_BATTLE_SCALING = true;
	public static boolean USE_AUTOMATED_DYNAMIC_SCALING = false;
	public static boolean USE_AUTOMATED_LEVEL_SCALING = false;

	public static float BATTLESIZE = Global.getSettings().getBattleSize();
	public static float THRESHOLD_DIVISOR = 10f;
	public static float AUTOMATED_POINTS_THRESHOLD_FULL = 120;
	//public static float BATTLESIZE_MULT = BATTLESIZE/300;
	//public static float DP_THRESHOLD = 30;
	//public static float FINAL_THRESHOLD = (DP_THRESHOLD*BATTLESIZE_MULT);
	
	public static float MAX_CR_BONUS = 80f;

	public static void refreshThreshold() {

		if (USE_AUTOMATED_BATTLE_SCALING) {
			BATTLESIZE = Global.getSettings().getBattleSize();
			BaseSkillEffectDescription.AUTOMATED_POINTS_THRESHOLD = (BATTLESIZE / THRESHOLD_DIVISOR);
		}
		else if (USE_AUTOMATED_LEVEL_SCALING) {
			if (Global.getSector() != null && Global.getSector().getPlayerStats() != null) {
				BaseSkillEffectDescription.AUTOMATED_POINTS_THRESHOLD = AUTOMATED_POINTS_THRESHOLD_FULL * 
					((float)Global.getSector().getPlayerStats().getLevel() / (float)Global.getSettings().getLevelupPlugin().getMaxLevel());
			} else {
				BaseSkillEffectDescription.AUTOMATED_POINTS_THRESHOLD = AUTOMATED_POINTS_THRESHOLD_FULL * 
						(1f / (float)Global.getSettings().getLevelupPlugin().getMaxLevel());
			}
		}
		else {
			//LoadQualityTechv2 initializes this to the custom value.
			//BaseSkillEffectDescription.AUTOMATED_POINTS_THRESHOLD = AUTOMATED_POINTS_THRESHOLD_FULL;
		}
	}
	
	
	public static class Level0 implements DescriptionSkillEffect {
		public String getString() {
			refreshThreshold();
			int alpha = Math.round(AICoreOfficerPluginImpl.ALPHA_MULT);
			int beta = Math.round(AICoreOfficerPluginImpl.BETA_MULT);
			int gamma = Math.round(AICoreOfficerPluginImpl.GAMMA_MULT);
			//if (BaseSkillEffectDescription.USE_RECOVERY_COST) {
			if (USE_AUTOMATED_LIMITS) {
				return "*总 \"无人舰点数\" 等于舰队中所有自动化舰船部署点的总和，但还需根据安装的 AI 核心乘以修正倍率 - " +
						alpha + Strings.X + "  (Alpha 核心)。" +			
						beta + Strings.X + "  (Beta 核心)。" +			
						gamma + Strings.X + "  (Gamma 核心)。"
						+ "因安全连锁系统的限制，带有 AI 核心的舰船，其 部署点 不会受到任何效果的影响。";
			} else {
				return "你能部署的自动化舰船数量不受限制。因安全连锁系统的限制，带有 AI 核心的舰船，其 部署点 不会受到任何效果的影响。";
			}
		}
		public Color[] getHighlightColors() {
			Color h = Misc.getHighlightColor();
			h = Misc.getDarkHighlightColor();
			Color bad = Misc.getNegativeHighlightColor();
			//bad = Misc.setAlpha(bad, 200);
			return new Color[] {h, h, h, bad};
		}
		public String[] getHighlights() {
			int alpha = (int) Math.round(AICoreOfficerPluginImpl.ALPHA_MULT);
			int beta = (int) Math.round(AICoreOfficerPluginImpl.BETA_MULT);
			int gamma = (int) Math.round(AICoreOfficerPluginImpl.GAMMA_MULT);
			return new String [] {"" + alpha + Strings.X, "" + beta + Strings.X, "" + gamma + Strings.X, 
					"不会受到任何效果的影响"};
		}
		public Color getTextColor() {
			return null;
		}
	}
	
	
	public static class Level1 extends BaseSkillEffectDescription implements ShipSkillEffect, FleetTotalSource {
		
		public FleetTotalItem getFleetTotalItem() {
			return getAutomatedPointsTotal();
		}
		
		public void apply(MutableShipStatsAPI stats, HullSize hullSize, String id, float level) {
			refreshThreshold();
			if (Misc.isAutomated(stats) && !Automated.isAutomatedNoPenalty(stats)) {
				float crBonus = 0f;
				if (USE_AUTOMATED_LIMITS) {
					crBonus = computeAndCacheThresholdBonus(stats, "auto_cr", MAX_CR_BONUS, ThresholdBonusType.AUTOMATED_POINTS);
				} else {
					crBonus = MAX_CR_BONUS;
				}
				SkillSpecAPI skill = Global.getSettings().getSkillSpec(Skills.AUTOMATED_SHIPS);
				stats.getMaxCombatReadiness().modifyFlat(id, crBonus * 0.01f, skill.getName() + " 技能");
			}
		}
			
		public void unapply(MutableShipStatsAPI stats, HullSize hullSize, String id) {
			stats.getMaxCombatReadiness().unmodifyFlat(id);
		}
		
		public String getEffectDescription(float level) {
			return null;
		}
			
		public void createCustomDescription(MutableCharacterStatsAPI stats, SkillSpecAPI skill, 
											TooltipMakerAPI info, float width) {
			init(stats, skill);
			
			FleetDataAPI data = getFleetData(null);
			float crBonus = computeAndCacheThresholdBonus(data, stats, "auto_cr", MAX_CR_BONUS, ThresholdBonusType.AUTOMATED_POINTS);
			
			if (USE_AUTOMATED_LIMITS) {
				info.addPara("+%s 自动化战舰战备值 (增益上限: %s)", 0f, hc, hc,
					"" + (int) crBonus + "%",
					"" + (int) MAX_CR_BONUS + "%");
				addAutomatedThresholdInfo(info, data, stats);
			} else {
				info.addPara("自动化战舰最多能恢复至 %s 战备值", 0f, hc, hc,
						"" + (int) MAX_CR_BONUS + "%");
				//addAutomatedThresholdInfo(info, data, stats);
			}
		}
		
		public ScopeDescription getScopeDescription() {
			return ScopeDescription.ALL_SHIPS;
		}
	}
	
	public static class Level2f extends BaseSkillEffectDescription implements CharacterStatsSkillEffect {

		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			if (stats.isPlayerStats()) {
				Misc.getAllowedRecoveryTags().add(Tags.AUTOMATED_RECOVERABLE);
			}
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			if (stats.isPlayerStats()) {
				Misc.getAllowedRecoveryTags().remove(Tags.AUTOMATED_RECOVERABLE);
			}
		}
		
		public void createCustomDescription(MutableCharacterStatsAPI stats, SkillSpecAPI skill, 
				TooltipMakerAPI info, float width) {
			init(stats, skill);
			info.addPara("允许恢复自动化舰船，如被遗弃的无人战舰", hc, 0f);
			info.addPara("自动化舰船只能由 AI 核心操控", hc, 0f);
			info.addSpacer(5f);
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.FLEET;
		}
	}
	
	public static class Level2 extends BaseSkillEffectDescription implements CharacterStatsSkillEffect {

		public void apply(MutableCharacterStatsAPI stats, String id, float level) {
			if (stats.isPlayerStats()) {
				Misc.getAllowedRecoveryTags().add(Tags.AUTOMATED_RECOVERABLE);
			}
		}

		public void unapply(MutableCharacterStatsAPI stats, String id) {
			if (stats.isPlayerStats()) {
				Misc.getAllowedRecoveryTags().remove(Tags.AUTOMATED_RECOVERABLE);
			}
		}
		
		public void createCustomDescription(MutableCharacterStatsAPI stats, SkillSpecAPI skill, 
				TooltipMakerAPI info, float width) {
			init(stats, skill);
			info.addPara("允许恢复自动化舰船，如被遗弃的无人战舰", hc, 0f);
			info.addPara("自动化舰船只能由 AI 核心操控", hc, 0f);
			if (USE_AUTOMATED_LIMITS && USE_AUTOMATED_BATTLE_SCALING) { 
				info.addPara("你的无人舰点数上限由你的战斗规模设置决定 / " + Math.round(THRESHOLD_DIVISOR), hc, 0f); 
			} else if (USE_AUTOMATED_LIMITS) {
				info.addPara("你的无人舰点数上限为 " + (int)BaseSkillEffectDescription.AUTOMATED_POINTS_THRESHOLD, hc, 0f); 
			}
			if (USE_AUTOMATED_LIMITS && USE_AUTOMATED_LEVEL_SCALING) {
				info.addPara("你的无人舰点数上限与你的等级成正比: " + (int)BaseSkillEffectDescription.AUTOMATED_POINTS_THRESHOLD + " (上限: " + (int)AUTOMATED_POINTS_THRESHOLD_FULL + ")", hc, 0f);
			}
			info.addSpacer(5f);
		}
		
		public String getEffectPerLevelDescription() {
			return null;
		}

		public ScopeDescription getScopeDescription() {
			return ScopeDescription.FLEET;
		}
	}

}





