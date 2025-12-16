package dal.impl.campaign.skills.milestones;

import java.io.IOException;

import com.fs.starfarer.api.Global;
import com.fs.starfarer.api.characters.FleetStatsSkillEffect;
import com.fs.starfarer.api.characters.MutableCharacterStatsAPI.SkillLevelAPI;
import com.fs.starfarer.api.fleet.MutableFleetStatsAPI;
import com.fs.starfarer.api.impl.campaign.ids.Stats;

public class CaptainsAcademician { //Galatia
	
	public static float SENSOR_PERC = 50f;
	
	public static boolean enabled = false;
	public static final String skillID = "captains_academician";
	public static final String skillName = "院士";
	public static final String skillDesc = "就算我们不考虑丰厚的佣金，追求知识本身就是一种回报。";
	public static final String skillAuthor = "Galatia 学院自由舰长";
	public static final String skillIcon = "/graphics/icons/skills/"+ skillID + ".png";
	
	public static class Level1 implements FleetStatsSkillEffect {

		public ScopeDescription getScopeDescription() {
			if (enabled) return ScopeDescription.FLEET;
			return ScopeDescription.NONE;
		}

		public String getEffectDescription(float level) {
			if (enabled) return "传感器强度 " + Math.round(SENSOR_PERC) + "%";
			return "";
		}

		public String getEffectPerLevelDescription() {
			// TODO Auto-generated method stub
			return null;
		}

		public void apply(MutableFleetStatsAPI stats, String id, float level) {
			stats.getSensorRangeMod().modifyPercent(id, SENSOR_PERC);
		}

		public void unapply(MutableFleetStatsAPI stats, String id) {
			stats.getSensorRangeMod().unmodifyPercent(id);
		}
	}
	
	public static void toggleMilestone() {
		for (SkillLevelAPI skill : Global.getSector().getPlayerStats().getSkillsCopy()) {
			if (skill.getSkill().getId().equals(skillID)) {
				if (skill.getLevel()==0) {
					skill.getSkill().setDescription(skillDesc);
					skill.getSkill().setAuthor(skillAuthor);
					skill.getSkill().setName(skillName);
					try {
						Global.getSettings().loadTexture(skillIcon);
					} catch (IOException e) {
						
					}
					skill.getSkill().setSpriteName(skillIcon);
					//skill.getSkill().getTags().remove("npc_only");
					skill.getSkill().setPermanent(true);
					skill.setLevel(1);
					enabled = true;
				} else {
					skill.getSkill().setDescription("开始追求更高层次的知识。");
					skill.getSkill().setAuthor("");
					skill.getSkill().setName("未来里程碑");
					try {
						Global.getSettings().loadTexture("graphics/icons/skills/blank.png");
					} catch (IOException e) {
						
					}
					skill.getSkill().setSpriteName("graphics/icons/skills/blank.png");				
					//skill.getSkill().addTag("npc_only");
					skill.getSkill().setPermanent(false);
					skill.setLevel(0);
					enabled = false;
				}
			}
		}
	}
	
	public static void enableDisable() {
		for (SkillLevelAPI skill : Global.getSector().getPlayerStats().getSkillsCopy()) {
			if (skill.getSkill().getId().equals(skillID)) {
				if (skill.getLevel() > 0) {
					skill.getSkill().setDescription(skillDesc);
					skill.getSkill().setAuthor(skillAuthor);
					skill.getSkill().setName(skillName);
					try {
						Global.getSettings().loadTexture(skillIcon);
					} catch (IOException e) {
						
					}
					skill.getSkill().setSpriteName(skillIcon);
					skill.getSkill().setPermanent(true);
					enabled = true;
				} else {
					skill.getSkill().setDescription("开始追求更高层次的知识。");
					skill.getSkill().setAuthor("");
					skill.getSkill().setName("未来里程碑");
					try {
						Global.getSettings().loadTexture("graphics/icons/skills/blank.png");
					} catch (IOException e) {
						
					}
					skill.getSkill().setSpriteName("graphics/icons/skills/blank.png");				
					skill.getSkill().setPermanent(false);
					enabled = false;
				}
			}
		}
	}
}



