package second_in_command.skills.misc

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.campaign.AICoreOfficerPlugin
import com.fs.starfarer.api.characters.*
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.fleet.FleetMemberAPI
import com.fs.starfarer.api.impl.campaign.ids.Strings
import com.fs.starfarer.api.impl.hullmods.Automated
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI.TooltipCreator
import com.fs.starfarer.api.util.Misc
import second_in_command.SCUtils
import second_in_command.misc.baseOrModSpec
import second_in_command.scripts.AutomatedShipsManager
import second_in_command.skills.automated.SCBaseAutoPointsSkillPlugin

class UtilitySkill : SCBaseVanillaShipSkill() {
    override fun getScopeDescription(): LevelBasedEffect.ScopeDescription {
        return LevelBasedEffect.ScopeDescription.PILOTED_SHIP
    }

    override fun createCustomDescription(stats: MutableCharacterStatsAPI?, skill: SkillSpecAPI?, info: TooltipMakerAPI?, width: Float) {


    }

    override fun apply(stats: MutableShipStatsAPI?, hullSize: ShipAPI.HullSize?, id: String?, level: Float) {
        if (Global.getSector()?.playerFleet?.fleetData != null) {
            for (skill in SCUtils.getPlayerData().getAllActiveSkillsPlugins()) {
                skill.callEffectsFromSeparateSkill(stats, hullSize, "${skill.id}_$id")
            }
        }
    }

    override fun unapply(stats: MutableShipStatsAPI?, hullSize: ShipAPI.HullSize?, id: String?) {

    }

    class AutomatedItem() : SCPlaceholderShipSkill(), FleetTotalSource {

        data class DPData(var member: FleetMemberAPI, var points: Int, var mult: Float)

        override fun getFleetTotalItem(): FleetTotalItem? {
            var fleet = Global.getSector()?.playerFleet ?: return FleetTotalItem()
            var manager = AutomatedShipsManager.get() ?: return FleetTotalItem()
            var data = SCUtils.getPlayerData()

            var used = manager.getUsedDP().toInt()
            var max = manager.getMaximumDP().toInt()

            var value = "失效"
            if (max != 0) value = "$used (上限 $max)"

            val item = FleetTotalItem()
            item.label = "自动化舰船"
            if (max == 0) item.valueColor = Misc.getGrayColor()
            item.value = value
            item.sortOrder = 350f

            item.tooltipCreator = object : TooltipCreator {
                override fun isTooltipExpandable(tooltipParam: Any?): Boolean {
                    return false
                }

                override fun getTooltipWidth(tooltipParam: Any?): Float {
                    return 450f
                }

                override fun createTooltip(tooltip: TooltipMakerAPI?, expanded: Boolean, tooltipParam: Any?) {




                    tooltip!!.addPara("需要具备特定技能才能运用和恢复自动化舰船。 " +
                            "启用时，显示你的舰队中所有自动化舰船的 总部署点数，以及所有生效技能提供的 无人舰点数上限。 ",
                        0f)

                    tooltip.addSpacer(10f)


                    //Show relevant skills here

                    var autoSkills = data.getAllActiveSkillsPlugins().filter { it is SCBaseAutoPointsSkillPlugin } as List<SCBaseAutoPointsSkillPlugin>
                    var extra = ""
                    if (autoSkills.isNotEmpty()) extra = "以下技能拓展了你的无人舰点数上限："

                    tooltip.addPara("自动化舰船的基础战备值惩罚可以被提供无人舰点数上限的技能所抵消。 " +
				"使用的无人舰点数若少于或等于 100%% 的可用无人舰点数上限，能够消除 100%% 的惩罚。 使用无人舰点数上限两倍的无人舰点数会使惩罚保留 50%%}。 $extra",
                        0f, Misc.getTextColor(), Misc.getHighlightColor(), "100%", "100%", "50%")


                    var stat = Global.getSector().playerPerson.stats.dynamic.getMod("sc_auto_dp")
                    var bonuses = stat.flatBonuses

                    if (bonuses.isNotEmpty()) tooltip.addSpacer(10f)




                    var entries = HashMap<String, Int>()

                    for (skill in autoSkills.sortedByDescending { it.getProvidedPoints() }) {
                        var points = skill.getProvidedPoints()

                        var autoString = "   +$points"
                        autoString += "   ${skill.name} "

                        entries.put(autoString, points)

                        //tooltip.addPara(autoString, 0f, Misc.getTextColor(), Misc.getHighlightColor(), "+$points")
                    }


                    for (bonus in bonuses) {
                        if (!bonus.key.contains("_external")) continue
                        var points = bonus.value.value.toInt()

                        var autoString = "   +$points"
                        autoString += "   ${bonus.value.desc}"

                        entries.put(autoString, points)

                        //tooltip.addPara(autoString, 0f, Misc.getTextColor(), Misc.getHighlightColor(), "+$points")
                    }

                    for (entry in entries.toList().sortedByDescending { it.second }) {
                        tooltip.addPara(entry.first, 0f, Misc.getTextColor(), Misc.getHighlightColor(), "+${entry.second}")
                    }


                    tooltip.addSpacer(10f)

                    tooltip.addPara("以下舰船消耗了无人舰点数，封存舰船不会造成影响。{AI 核心}和{其他因素}在计算时会对部署点数实施倍率乘算。 ",
                        0f, Misc.getTextColor(), Misc.getHighlightColor(), "AI 核心", "其他因素")

                    tooltip.addSpacer(10f)

                    //Auto points

                    var autoShips = ArrayList<DPData>()

                    for (curr in fleet.fleetData.membersListCopy) {
                        if (curr.isMothballed) continue
                        if (!Misc.isAutomated(curr)) continue
                        if (Automated.isAutomatedNoPenalty(curr)) continue
                        var mult = 1f
                        var points = curr.captain.memoryWithoutUpdate.getFloat(AICoreOfficerPlugin.AUTOMATED_POINTS_VALUE)
                        mult = curr.captain.memoryWithoutUpdate.getFloat(AICoreOfficerPlugin.AUTOMATED_POINTS_MULT)

                        if (mult == 0f) mult = 1f

                        var memberMult = curr.stats.dynamic.getStat("sc_auto_points_mult").modifiedValue
                        mult *= memberMult

                        points += Math.round(curr.deploymentPointsCost * mult).toFloat()

                        var data = DPData(curr, points.toInt(), mult)
                        autoShips.add(data)
                    }

                    var maxEntries = 15
                    var entryCount = 0

                    for (autoData in ArrayList(autoShips.sortedByDescending { it.points })) {

                        entryCount++
                        if (entryCount >= maxEntries) break

                        autoShips.remove(autoData)

                        var points = autoData.points
                        var mult = autoData.mult
                        var member = autoData.member

                        var multString = String.format("%.2f", mult)

                        tooltip.addPara("   +$points   ${member.shipName}, ${member.baseOrModSpec().hullName}-级 (${multString}${Strings.X})",
                            0f, Misc.getTextColor(), Misc.getHighlightColor(), "+$points", "${multString}${Strings.X}")
                    }

                    //Prevent displaying way to many ships if there are tons of automated ships
                    if (autoShips.isNotEmpty()) {
                        var points = autoShips.sumOf { it.points }
                        tooltip.addPara("   其他舰船 +$points 点", 0f,
                            Misc.getTextColor(), Misc.getHighlightColor(), "+$points")
                    }

                }

            }

            return item
        }
    }

}