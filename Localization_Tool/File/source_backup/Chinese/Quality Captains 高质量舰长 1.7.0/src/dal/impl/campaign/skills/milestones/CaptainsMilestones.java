package dal.impl.campaign.skills.milestones;

import java.awt.Color;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.characters.DescriptionSkillEffect;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI.SkillLevelAPI;
import com.fs.starfarer.api.impl.campaign.intel.BaseIntelPlugin;
import com.fs.starfarer.api.util.Misc;

public class CaptainsMilestones {
	public static class Level0 implements DescriptionSkillEffect {
		public String getString() {
			//return "The maximum level of all skills governed by this aptitude is limited to the level of the aptitude.";
			return BaseIntelPlugin.BULLET + "这些技能会在特定事件后自动获得。\n"
				  + BaseIntelPlugin.BULLET + "\n由于原版限制，生效的里程碑可能会导致无法正常重新分配技能。" 
				  + "解决方法：关闭里程碑开关，等待其消失，重新分配技能后再开启里程碑开关。"
				;
		}
		public Color[] getHighlightColors() {
			Color h = Misc.getHighlightColor();
			Color s = Misc.getStoryOptionColor();
			return new Color[] {h, h, h, s};
		}
		public String[] getHighlights() {
			return new String[] {""};
		}
		public Color getTextColor() {
			return Misc.getTextColor();
			//return null;
		}
	}
	
	public static Boolean hasSkill(String skillID) {
		for (SkillLevelAPI skill : Global.getSector().getPlayerStats().getSkillsCopy()) {
			if (skill.getSkill().getId() == skillID && skill.getLevel() > 0) {
				return true;
			}
		}
		return false;
	}
		
//		public static class CombatDesc implements DescriptionSkillEffect {
//			public String getString() {
//				return "The maximum level of all skills governed by this aptitude is limited to the level of the aptitude.";
////				return "The maximum level of all skills governed by this aptitude is limited to the level of the aptitude." +
////						"\n\n" + 
////						"All combat skills have a Mastery effect that applies to all ships in the fleet, including your flagship, " +
////						"when the skill reaches level three.";
//			}
//			public Color[] getHighlightColors() {
//				Color c = Global.getSettings().getColor("tooltipTitleAndLightHighlightColor"); 
//				return new Color[] {c};
//			}
//			public String[] getHighlights() {
//				return new String[] {"Mastery"};
//			}
//			public Color getTextColor() {
//				return null;
//			}
//		}

		
}
